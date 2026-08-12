from pathlib import Path

import pytest

from tests.database_safety import require_test_database, require_test_env_file


def test_requires_env_file(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match=r"Missing \.env\.test file"):
        require_test_env_file(tmp_path / ".env.test")


def test_rejects_non_test_database() -> None:
    with pytest.raises(RuntimeError, match="database 'app'"):
        require_test_database("postgresql+asyncpg://postgres:postgres@localhost/app")


def test_accepts_test_database_with_query_parameters() -> None:
    require_test_database("postgresql+asyncpg://postgres:postgres@localhost/app_test?ssl=false")
