"""The test-cleanup list must cover everything that points at `users`.

`_TABLES_TO_CLEAN` deliberately excludes `users`: the super_admin/editor/viewer
accounts have to survive the whole session. But several tests *do* delete user
rows — the bootstrap suite deletes every super_admin to prove bootstrap
recreates it. PostgreSQL then refuses that delete if any child row still points
at the user, while SQLite, which does not enforce foreign keys by default,
allows it.

The failure this prevents is deliberately misleading. It does not surface in
the test that left the child row behind; it surfaces later, in an unrelated
test that deletes a user, as a foreign key on a table that test never touched.
Fixing the constraint named in the traceback just reveals the next one behind
it — which is how this was found: adding `password_reset_tokens` moved the
failure to `api_keys`.

So the invariant is asserted over the whole schema rather than one constraint
at a time.
"""

from __future__ import annotations

import pathlib
import re

from backend import models

_CONFTEST = pathlib.Path(__file__).parent / "conftest.py"


def _cleaned_tables() -> set[str]:
    """The table names listed in conftest's `_TABLES_TO_CLEAN`.

    Parsed from the source rather than imported: importing conftest for its
    constants would re-run its module-level database setup.
    """
    source = _CONFTEST.read_text(encoding="utf-8")
    block = source.split("_TABLES_TO_CLEAN = [")[1].split("]")[0]
    return set(re.findall(r'"([a-z_]+)"', block))


def _tables_referencing(target: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for table in models.Base.metadata.tables.values():
        for fk in table.foreign_keys:
            if fk.column.table.name == target:
                found.setdefault(table.name, []).append(fk.parent.name)
    return found


def test_every_table_referencing_users_is_cleaned():
    referencing = _tables_referencing("users")
    assert referencing, "expected some table to reference users — the query is wrong"

    cleaned = _cleaned_tables()
    missing = sorted(set(referencing) - cleaned)

    assert not missing, (
        "These tables have a foreign key to `users` but are not in "
        "`_TABLES_TO_CLEAN`, so a leftover row in any of them makes an "
        "unrelated test's user delete fail on PostgreSQL:\n  "
        + "\n  ".join(f"{t} (via {', '.join(referencing[t])})" for t in missing)
        + "\n\nAdd them to _TABLES_TO_CLEAN in backend/tests/conftest.py."
    )


def test_cleanup_list_has_no_dead_entries():
    """A name that matches no table protects nothing and hides a typo.

    Without this, renaming a table silently drops it from cleanup: the DELETE
    is issued against a table that no longer exists, `_delete_test_table`
    swallows the error, and the gap only shows up as a foreign key violation
    somewhere unrelated.
    """
    known = set(models.Base.metadata.tables)
    # `search_index` is created by conftest as raw DDL (FTS5 on SQLite, a plain
    # table on PostgreSQL), so it is real but never appears in the metadata.
    known.add("search_index")
    dead = sorted(_cleaned_tables() - known)
    assert not dead, f"_TABLES_TO_CLEAN names tables that do not exist: {dead}"
