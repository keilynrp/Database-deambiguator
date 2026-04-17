import pytest

from backend import models
from backend.bootstrap import ensure_bootstrap_super_admin


@pytest.mark.usefixtures("db_session")
def test_bootstrap_creates_super_admin_when_missing(db_session, monkeypatch):
    existing_super_admin = (
        db_session.query(models.User)
        .filter(models.User.role == "super_admin")
        .all()
    )
    for user in existing_super_admin:
        db_session.delete(user)
    db_session.commit()

    monkeypatch.setenv("ADMIN_USERNAME", "superadmin")
    monkeypatch.setenv("ADMIN_PASSWORD", "supersecret123")
    monkeypatch.delenv("ADMIN_PASSWORD_HASH", raising=False)

    ensure_bootstrap_super_admin(db_session)

    user = db_session.query(models.User).filter(models.User.username == "superadmin").first()
    assert user is not None
    assert user.role == "super_admin"
    assert user.is_active is True
    assert user.password_hash != "supersecret123"


@pytest.mark.usefixtures("db_session")
def test_bootstrap_repairs_missing_super_admin_role(db_session, monkeypatch):
    existing_super_admin = (
        db_session.query(models.User)
        .filter(models.User.role == "super_admin")
        .all()
    )
    for user in existing_super_admin:
        db_session.delete(user)
    db_session.commit()

    monkeypatch.setenv("ADMIN_USERNAME", "bootstrap_admin")
    monkeypatch.setenv("ADMIN_PASSWORD_HASH", "prehashed-secret")
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    db_session.add(models.User(
        username="bootstrap_admin",
        password_hash="old-hash",
        role="viewer",
        is_active=False,
    ))
    db_session.commit()

    ensure_bootstrap_super_admin(db_session)

    user = db_session.query(models.User).filter(models.User.username == "bootstrap_admin").first()
    assert user is not None
    assert user.role == "super_admin"
    assert user.is_active is True
    assert user.password_hash == "prehashed-secret"


@pytest.mark.usefixtures("db_session")
def test_bootstrap_is_noop_when_another_super_admin_exists(db_session, monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "secondary_admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "another-secret123")
    monkeypatch.delenv("ADMIN_PASSWORD_HASH", raising=False)

    ensure_bootstrap_super_admin(db_session)

    user = db_session.query(models.User).filter(models.User.username == "secondary_admin").first()
    assert user is None
