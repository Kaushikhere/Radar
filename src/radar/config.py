"""Settings read from environment variables."""

import os

DEFAULT_DATABASE_URL = "postgresql+psycopg://radar:radar@localhost:5432/radar"


def database_url() -> str:
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
