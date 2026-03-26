import os


def default_database_url() -> str:
    db_mode = os.environ.get("UKIP_DB_MODE", "postgres").lower()
    if db_mode == "sqlite":
        return os.environ.get("SQLITE_DATABASE_URL", "sqlite:///./sql_app.db")

    pg_user = os.environ.get("POSTGRES_USER", "ukip")
    pg_password = os.environ.get("POSTGRES_PASSWORD", "ukip_secret")
    pg_host = os.environ.get("POSTGRES_HOST", "127.0.0.1")
    pg_port = os.environ.get("POSTGRES_PORT", "5432")
    pg_db = os.environ.get("POSTGRES_DB", "ukip")
    return f"postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"


def resolve_database_url() -> str:
    return os.environ.get("DATABASE_URL") or default_database_url()
