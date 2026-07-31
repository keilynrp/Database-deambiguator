"""Give the raw_entities back-references an ON DELETE action — issue #216.

Both FKs pointing at ``raw_entities`` were created with no ``ondelete``, and
``models.py`` declares no ORM ``relationship()`` anywhere, so nothing cascaded at
either layer. Deleting an entity that had a single relationship row raised a FK
violation, surfacing as a 500 from both delete endpoints. Auto-resolve-on-ingest
and the semantic-keyword engine write those rows within seconds of an import, so
in practice imported entities became undeletable almost immediately.

The two references get different actions on purpose:

* ``entity_relationships`` → CASCADE. Derived graph edges, rewritten by the
  engines that produced them; nothing of record is lost.
* ``harmonization_change_records`` → SET NULL. Audit history: which field
  changed, from what, to what. Cascading it would let deleting an entity destroy
  the evidence that someone edited it. The column is already nullable, every
  reader filters by ``log_id``, and the undo path guards with ``if entity:``.

Revision ID: d1e2f3a4b5c6
Revises: c1d2e3f4a5b6
"""
from alembic import op
import sqlalchemy as sa

revision = "d1e2f3a4b5c6"
down_revision = "c1d2e3f4a5b6"
branch_labels = None
depends_on = None


# (table, column, ondelete action to install)
#
# Derived or operational rows cascade; anything a human authored keeps its row
# and loses only the reference.
#
# The last two are not declared in models.py at all — `annotations.entity_id` is
# a bare Integer with a `# FK raw_entities.id` comment, and enrichment_queue's
# constraint likewise exists only in the database. Reading the models would
# never have found them; they turned up by inspecting pg_constraint on a real
# Postgres schema. Fixing only the declared pair would have left entities with
# an annotation or a queued enrichment just as undeletable as before.
_TARGETS = [
    ("entity_relationships", "source_id", "CASCADE"),
    ("entity_relationships", "target_id", "CASCADE"),
    ("harmonization_change_records", "record_id", "SET NULL"),
    ("annotations", "entity_id", "SET NULL"),
    # entity_id is NOT NULL here, so SET NULL is not available — and a queued
    # enrichment task for a deleted entity has nothing left to enrich.
    ("enrichment_queue", "entity_id", "CASCADE"),
]


def _existing_fk_name(conn, table: str, column: str) -> str | None:
    """Look the constraint up rather than assuming Postgres' default naming.

    These tables were created across several migrations; hardcoding
    ``<table>_<column>_fkey`` would fail silently on any that was named
    explicitly.
    """
    inspector = sa.inspect(conn)
    for fk in inspector.get_foreign_keys(table):
        if fk.get("constrained_columns") == [column] and fk.get("referred_table") == "raw_entities":
            return fk.get("name")
    return None


def _rebuild(conn, table: str, column: str, ondelete: str | None) -> None:
    name = _existing_fk_name(conn, table, column)
    if name:
        op.drop_constraint(name, table, type_="foreignkey")
    op.create_foreign_key(
        f"fk_{table}_{column}_raw_entities",
        table,
        "raw_entities",
        [column],
        ["id"],
        ondelete=ondelete,
    )


def upgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "sqlite":
        # SQLite cannot ALTER a foreign key; the table would have to be rebuilt.
        # Test databases are built from models metadata rather than migrations,
        # so they already carry the ondelete clause and need nothing here.
        return
    for table, column, action in _TARGETS:
        _rebuild(conn, table, column, action)


def downgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "sqlite":
        return
    for table, column, _ in _TARGETS:
        _rebuild(conn, table, column, None)
