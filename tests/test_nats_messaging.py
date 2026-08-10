import json
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock

import pytest
from pytest import MonkeyPatch

from app.config.settings import get_settings
from app.shared.messaging.nats_client import NatsJetStreamService


def test_nats_naming_uses_governed_prefixes(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("NATS_SUBJECT_PREFIX", "templates")
    monkeypatch.setenv("NATS_STREAM_PREFIX", "template")
    get_settings.cache_clear()
    service = NatsJetStreamService()

    try:
        assert service.get_subject("orders:created") == "templates.orders.created"
        assert service.get_dead_letter_subject("orders:created") == "templates.orders.created.dlq"
        assert service.get_stream_name("orders:created") == "TEMPLATE_ORDERS_CREATED"
        assert service.get_consumer_name("order-service") == "order-service"
    finally:
        get_settings.cache_clear()


@pytest.mark.asyncio
async def test_stream_and_consumer_configuration_is_reconciled(monkeypatch: MonkeyPatch) -> None:
    service = NatsJetStreamService()
    jetstream = AsyncMock()
    monkeypatch.setattr(service, "jetstream", AsyncMock(return_value=jetstream))

    stream_name = await service.ensure_stream("orders:created")

    assert stream_name == "TEMPLATE_ORDERS_CREATED"
    jetstream.stream_info.assert_awaited_once_with(stream_name)
    stream_config = jetstream.update_stream.await_args.args[0]
    assert stream_config.name == stream_name
    assert stream_config.subjects == ["templates.orders.created", "templates.orders.created.dlq"]

    monkeypatch.setattr(service, "ensure_stream", AsyncMock(return_value=stream_name))
    consumer_name = await service.ensure_consumer("orders:created", "order-service")

    assert consumer_name == "order-service"
    jetstream.consumer_info.assert_awaited_once_with(stream_name, consumer_name)


@pytest.mark.asyncio
async def test_health_and_close_cover_success_and_failure_paths(monkeypatch: MonkeyPatch) -> None:
    disconnected_service = NatsJetStreamService()
    await disconnected_service.close()
    monkeypatch.setattr(disconnected_service, "connect", AsyncMock())
    with pytest.raises(RuntimeError, match="JetStream context is unavailable"):
        await disconnected_service.jetstream()

    service = NatsJetStreamService()
    jetstream = AsyncMock()
    monkeypatch.setattr(service, "jetstream", AsyncMock(return_value=jetstream))

    assert await service.is_healthy() is True
    jetstream.account_info.assert_awaited_once()

    monkeypatch.setattr(service, "jetstream", AsyncMock(side_effect=RuntimeError("unavailable")))
    assert await service.is_healthy() is False

    client = AsyncMock()
    service._client = client
    service._jetstream = jetstream
    await service.close()

    client.drain.assert_awaited_once()
    client.close.assert_awaited_once()
    assert service._client is None
    assert service._jetstream is None


@pytest.mark.asyncio
async def test_publish_writes_governed_envelope_and_idempotency_header(monkeypatch: MonkeyPatch) -> None:
    service = NatsJetStreamService()
    published: dict[str, Any] = {}

    class FakeAck:
        stream = "TEMPLATE_ORDERS_CREATED"
        seq = 42

    class FakeJetStream:
        async def publish(
            self,
            subject: str,
            payload: bytes,
            *,
            stream: str,
            headers: dict[str, str],
            timeout: float,
        ) -> FakeAck:
            published.update(
                {
                    "headers": headers,
                    "payload": json.loads(payload.decode()),
                    "stream": stream,
                    "subject": subject,
                    "timeout": timeout,
                }
            )
            return FakeAck()

    async def fake_ensure_stream(stream: str) -> str:
        assert stream == "orders:created"
        return "TEMPLATE_ORDERS_CREATED"

    async def fake_jetstream() -> FakeJetStream:
        return FakeJetStream()

    monkeypatch.setattr(service, "ensure_stream", fake_ensure_stream)
    monkeypatch.setattr(service, "jetstream", fake_jetstream)

    message_id = await service.publish(
        "orders:created",
        {"orderId": "order-1"},
        event_type="orders.created",
        source="orders-service",
        data_version="2",
        idempotency_key="event-1",
    )

    assert message_id == "TEMPLATE_ORDERS_CREATED:42"
    assert published["subject"] == "templates.orders.created"
    assert published["stream"] == "TEMPLATE_ORDERS_CREATED"
    assert published["headers"] == {"Nats-Msg-Id": "event-1"}
    assert published["payload"]["id"] == "event-1"
    assert published["payload"]["type"] == "orders.created"
    assert published["payload"]["source"] == "orders-service"
    assert published["payload"]["dataVersion"] == "2"
    assert published["payload"]["data"] == {"orderId": "order-1"}
    assert datetime.fromisoformat(published["payload"]["time"])


@pytest.mark.asyncio
async def test_handle_message_acks_successful_payload() -> None:
    service = NatsJetStreamService()
    handled: list[Any] = []

    class FakeMessage:
        data = json.dumps(
            {
                "id": "event-1",
                "type": "orders.created",
                "source": "orders-service",
                "time": "2026-06-13T00:00:00+00:00",
                "dataVersion": "1",
                "data": {"orderId": "order-1"},
            }
        ).encode()
        acked = False
        naked = False

        async def ack(self) -> None:
            self.acked = True

        async def nak(self) -> None:
            self.naked = True

    async def handler(payload: Any) -> None:
        handled.append(payload)

    message: Any = FakeMessage()
    await service._handle_message("orders:created", message, handler, lambda payload: isinstance(payload, dict))

    assert handled == [{"orderId": "order-1"}]
    assert message.acked is True
    assert message.naked is False


@pytest.mark.asyncio
async def test_handle_message_naks_failed_payload() -> None:
    service = NatsJetStreamService()

    class FakeMessage:
        data = json.dumps(
            {
                "id": "event-1",
                "type": "orders.created",
                "source": "orders-service",
                "time": "2026-06-13T00:00:00+00:00",
                "dataVersion": "1",
                "data": {"orderId": "order-1"},
            }
        ).encode()
        acked = False
        naked = False

        async def ack(self) -> None:
            self.acked = True

        async def nak(self) -> None:
            self.naked = True

    async def handler(_payload: Any) -> None:
        raise RuntimeError("forced failure")

    message: Any = FakeMessage()
    await service._handle_message("orders:created", message, handler, None)

    assert message.acked is False
    assert message.naked is True
