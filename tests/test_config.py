from radar.config import DEFAULT_DATABASE_URL, database_url


def test_database_url_defaults_when_unset(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    assert database_url() == DEFAULT_DATABASE_URL


def test_database_url_reads_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@host:5432/db")

    assert database_url() == "postgresql+psycopg://u:p@host:5432/db"
