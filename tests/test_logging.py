import logging

import pytest

from app.shared.logging.config import configure_logging, get_logger


@pytest.mark.parametrize("json_output", [False, True])
def test_configure_logging_supports_console_and_json_renderers(json_output: bool) -> None:
    configure_logging("warning", json_output=json_output)

    root_logger = logging.getLogger()
    assert root_logger.level == logging.WARNING
    assert len(root_logger.handlers) == 1
    assert get_logger("test") is not None

    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        assert logging.getLogger(name).propagate is True
