"""F5.1 — legacy CO_AUTHOR cleanup script tests."""
from backend import models
from backend.scripts.cleanup_legacy_coauthor import run


def _entities(db, n=2):
    """Create the entities the relationships point at.

    These used to hardcode `source_id=1, target_id=2` with no rows behind them.
    SQLite does not enforce foreign keys by default so the inserts succeeded;
    PostgreSQL rejects them, which is also what production would do.
    """
    rows = [
        models.RawEntity(primary_label=f"Entity {i}", domain="science", source="test")
        for i in range(n)
    ]
    db.add_all(rows)
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


def test_cleanup_deletes_only_coauthor_rows(db):
    a, b = _entities(db)
    db.add(models.EntityRelationship(source_id=a.id, target_id=a.id, relation_type="CO_AUTHOR",
                                     notes="a||b", weight=1.0))
    db.add(models.EntityRelationship(source_id=a.id, target_id=b.id, relation_type="REFERENCES",
                                     notes="ref", weight=1.0))
    db.commit()

    deleted = run(db)
    assert deleted == 1
    assert db.query(models.EntityRelationship).filter_by(relation_type="CO_AUTHOR").count() == 0
    assert db.query(models.EntityRelationship).filter_by(relation_type="REFERENCES").count() == 1


def test_cleanup_dry_run_counts_without_deleting(db):
    (a,) = _entities(db, n=1)
    db.add(models.EntityRelationship(source_id=a.id, target_id=a.id, relation_type="CO_AUTHOR",
                                     notes="a||b", weight=1.0))
    db.commit()
    n = run(db, dry_run=True)
    assert n == 1
    assert db.query(models.EntityRelationship).filter_by(relation_type="CO_AUTHOR").count() == 1
