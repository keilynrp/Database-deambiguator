from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from backend.db_config import resolve_database_url

# Alembic Config object
config = context.config

# Set up loggers from ini file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── UKIP: use the same PostgreSQL-first resolution path as the runtime ────────
_db_url = resolve_database_url()
config.set_main_option("sqlalchemy.url", _db_url)

# ── UKIP: import all models so autogenerate can detect schema changes ─────────
from backend import models  # noqa: E402 — must come after sys.path is set
from backend.database import Base  # noqa: E402

target_metadata = Base.metadata

# SQLite-specific: render AS NULL for server defaults so autogenerate diffs
# stay clean on SQLite (which ignores server-side default expressions).
_is_sqlite = _db_url.startswith("sqlite")

# Exclude FTS5 shadow tables (SQLite internal) and alembic_version from
# autogenerate so that `alembic check` / `--autogenerate` stays clean.
_FTS5_PREFIXES = ("search_index_", "search_index")
_EXCLUDED_TABLES = {"alembic_version"}


def _include_object(obj, name, type_, reflected, compare_to):
    if type_ == "table":
        if name in _EXCLUDED_TABLES:
            return False
        if any(name.startswith(p) for p in _FTS5_PREFIXES):
            return False
    return True


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (generates SQL output)."""
    context.configure(
        url=_db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=_is_sqlite,
        include_object=_include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live DB connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=_is_sqlite,
            include_object=_include_object,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
