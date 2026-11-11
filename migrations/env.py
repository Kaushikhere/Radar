"""Alembic environment. Reads the database URL from radar.config."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from radar.config import database_url

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Migrations are written by hand from the SQL in doc/PLAN.md, so there is no
# model metadata to autogenerate from.
target_metadata = None


def run_migrations_offline() -> None:
    context.configure(url=database_url(), literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(database_url())
    with engine.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
