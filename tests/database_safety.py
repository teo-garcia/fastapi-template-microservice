from pathlib import Path
from urllib.parse import unquote, urlsplit


def require_test_env_file(env_test_path: Path) -> None:
    if not env_test_path.is_file():
        raise RuntimeError("Missing .env.test file. Copy .env.test.example to .env.test before running database tests.")


def require_test_database(database_url: str) -> None:
    database_name = unquote(urlsplit(database_url).path.rsplit("/", 1)[-1])
    if not database_name.endswith("_test"):
        raise RuntimeError(
            f"Refusing to run destructive test setup against database {database_name!r}. "
            "DATABASE_URL must point to a database whose name ends in '_test'."
        )
