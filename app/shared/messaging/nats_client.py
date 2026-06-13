import asyncio
import re
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

import nats
import structlog
from nats.aio.client import Client as NatsClient
from nats.aio.msg import Msg
from nats.errors import TimeoutError as NatsTimeoutError
from nats.js import JetStreamContext
from nats.js.api import AckPolicy, ConsumerConfig, PubAck, StorageType, StreamConfig
from nats.js.errors import NotFoundError

from app.config.settings import get_settings
from app.shared.messaging.envelope import JetStreamEnvelope

logger = structlog.get_logger("nats")
T = TypeVar("T")


class NatsJetStreamService:
    def __init__(self) -> None:
        self._client: NatsClient | None = None
        self._connect_lock = asyncio.Lock()
        self._jetstream: JetStreamContext | None = None

    async def connect(self) -> NatsClient:
        if self._client and self._client.is_connected:
            return self._client

        async with self._connect_lock:
            if self._client and self._client.is_connected:
                return self._client

            settings = get_settings()
            self._client = await nats.connect(
                settings.nats_url,
                name=settings.nats_client_name,
                connect_timeout=settings.nats_timeout,
                max_reconnect_attempts=settings.nats_max_reconnect_attempts,
                reconnect_time_wait=settings.nats_reconnect_time_wait,
            )
            self._jetstream = self._client.jetstream(timeout=settings.nats_timeout)
            connected_url = self._client.connected_url
            await logger.ainfo(
                "nats_connected",
                server=connected_url.netloc if connected_url else settings.nats_url,
            )
            return self._client

    async def jetstream(self) -> JetStreamContext:
        if not self._jetstream:
            await self.connect()

        if not self._jetstream:
            msg = "NATS JetStream context is unavailable"
            raise RuntimeError(msg)

        return self._jetstream

    async def ensure_stream(self, stream: str) -> str:
        settings = get_settings()
        js = await self.jetstream()
        stream_name = self.get_stream_name(stream)
        subject = self.get_subject(stream)
        config = StreamConfig(
            name=stream_name,
            subjects=[subject, self.get_dead_letter_subject(stream)],
            storage=StorageType.FILE,
            max_msgs=settings.nats_max_messages,
        )

        try:
            await js.stream_info(stream_name)
            await js.update_stream(config)
        except NotFoundError:
            await js.add_stream(config)
            await logger.ainfo("nats_stream_created", stream=stream_name, subject=subject)

        return stream_name

    async def ensure_consumer(self, stream: str, consumer_group: str) -> str:
        settings = get_settings()
        js = await self.jetstream()
        stream_name = await self.ensure_stream(stream)
        consumer_name = self.get_consumer_name(consumer_group)
        config = ConsumerConfig(
            durable_name=consumer_name,
            ack_policy=AckPolicy.EXPLICIT,
            ack_wait=settings.nats_ack_wait_seconds,
            max_deliver=settings.nats_max_deliver,
            filter_subject=self.get_subject(stream),
        )

        try:
            await js.consumer_info(stream_name, consumer_name)
        except NotFoundError:
            await js.add_consumer(stream_name, config)
            await logger.ainfo(
                "nats_consumer_created",
                stream=stream_name,
                consumer=consumer_name,
            )

        return consumer_name

    async def publish(
        self,
        stream: str,
        data: Any,
        *,
        event_type: str | None = None,
        source: str | None = None,
        data_version: str = "1",
        idempotency_key: str | None = None,
    ) -> str:
        settings = get_settings()
        stream_name = await self.ensure_stream(stream)
        subject = self.get_subject(stream)
        envelope_data: dict[str, Any] = {
            "type": event_type or stream.replace(":", "."),
            "source": source or settings.nats_client_name,
            "dataVersion": data_version,
            "data": data,
        }
        if idempotency_key:
            envelope_data["id"] = idempotency_key

        envelope = JetStreamEnvelope(**envelope_data)
        payload = envelope.model_dump_json(by_alias=True).encode()
        js = await self.jetstream()
        ack: PubAck = await js.publish(
            subject,
            payload,
            stream=stream_name,
            headers={"Nats-Msg-Id": envelope.id},
            timeout=settings.nats_timeout,
        )
        return f"{ack.stream}:{ack.seq}"

    async def subscribe(
        self,
        stream: str,
        consumer_group: str,
        handler: Callable[[Any], Awaitable[None]],
        *,
        batch: int = 1,
        timeout: float = 5.0,
        validate: Callable[[Any], bool] | None = None,
    ) -> None:
        js = await self.jetstream()
        stream_name = await self.ensure_stream(stream)
        consumer_name = await self.ensure_consumer(stream, consumer_group)
        subscription = await js.pull_subscribe(
            self.get_subject(stream),
            durable=consumer_name,
            stream=stream_name,
        )

        while True:
            try:
                messages = await subscription.fetch(batch=batch, timeout=timeout)
            except NatsTimeoutError:
                continue

            for message in messages:
                await self._handle_message(stream, message, handler, validate)

    async def is_healthy(self) -> bool:
        try:
            js = await self.jetstream()
            await js.account_info()
            return True
        except Exception as exc:
            await logger.awarning("nats_health_check_failed", error=str(exc))
            return False

    async def close(self) -> None:
        if not self._client:
            return

        try:
            await self._client.drain()
        finally:
            await self._client.close()
            self._client = None
            self._jetstream = None

    def get_stream_name(self, stream: str) -> str:
        prefix = get_settings().nats_stream_prefix
        return f"{prefix}_{self._sanitize_name(stream)}".upper()

    def get_subject(self, stream: str) -> str:
        prefix = get_settings().nats_subject_prefix
        return f"{prefix}.{stream.replace(':', '.')}"

    def get_dead_letter_subject(self, stream: str) -> str:
        return f"{self.get_subject(stream)}.dlq"

    def get_consumer_name(self, name: str) -> str:
        return self._sanitize_name(name)

    async def _handle_message(
        self,
        stream: str,
        message: Msg,
        handler: Callable[[Any], Awaitable[None]],
        validate: Callable[[Any], bool] | None,
    ) -> None:
        try:
            envelope = JetStreamEnvelope.model_validate_json(message.data)
            payload = envelope.data
            if validate and not validate(payload):
                msg = "Invalid message payload"
                raise ValueError(msg)

            await handler(payload)
            await message.ack()
        except Exception as exc:
            await logger.aerror("nats_message_failed", stream=stream, error=str(exc))
            await message.nak()

    def _sanitize_name(self, name: str) -> str:
        return re.sub(r"[^A-Za-z0-9_-]", "_", name)


nats_service = NatsJetStreamService()


def get_nats() -> NatsJetStreamService:
    return nats_service
