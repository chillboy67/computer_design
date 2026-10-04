import bcrypt
from sqlalchemy import inspect, text

from base import Base
from db_utils import SessionLocal, init_db
from models import User
from user_service import UserService


def test_create_and_verify_user(fresh_db):
    assert UserService.create_user("alice", "secret123", "alice@example.com")
    assert UserService.user_exists("alice")
    assert UserService.verify_user("alice", "secret123")
    assert not UserService.verify_user("alice", "wrong-password")
    assert not UserService.verify_user("nobody", "secret123")


def test_duplicate_username_is_rejected(fresh_db):
    assert UserService.create_user("alice", "secret123")
    assert not UserService.create_user("alice", "another123")


def test_password_is_not_stored_in_plain_text(fresh_db):
    UserService.create_user("alice", "secret123")
    with SessionLocal() as session:
        user = session.query(User).filter_by(username="alice").one()
    assert "secret123" not in user.password_hash


def test_verify_legacy_bytes_hash(fresh_db):
    """旧版本把 bcrypt 结果以 bytes 形式写入数据库，需要继续兼容"""
    with SessionLocal() as session:
        session.add(User(username="legacy", password_hash=bcrypt.hashpw(b"oldpass", bcrypt.gensalt())))
        session.commit()
    assert UserService.verify_user("legacy", "oldpass")


def test_verify_non_bcrypt_hash_returns_false(fresh_db):
    with SessionLocal() as session:
        session.add(User(username="sha", password_hash="a" * 64))
        session.commit()
    assert not UserService.verify_user("sha", "anything")


def test_remember_token_lifecycle(fresh_db):
    UserService.create_user("alice", "secret123")
    token = UserService.issue_remember_token("alice")
    assert token
    assert UserService.verify_remember_token("alice", token)
    assert not UserService.verify_remember_token("alice", "forged-token")
    assert not UserService.verify_remember_token("bob", token)

    # 重新签发后旧令牌失效
    new_token = UserService.issue_remember_token("alice")
    assert not UserService.verify_remember_token("alice", token)
    assert UserService.verify_remember_token("alice", new_token)

    UserService.clear_remember_token("alice")
    assert not UserService.verify_remember_token("alice", new_token)


def test_issue_token_for_unknown_user(fresh_db):
    assert UserService.issue_remember_token("nobody") is None


def test_validate_registration():
    assert UserService.validate_registration("alice", "", "secret123") is None
    assert UserService.validate_registration("张三", "a@b.cn", "secret123") is None
    assert UserService.validate_registration("a", "", "secret123")
    assert UserService.validate_registration("bad name", "", "secret123")
    assert UserService.validate_registration("alice", "not-an-email", "secret123")
    assert UserService.validate_registration("alice", "", "123")


def test_init_db_upgrades_old_schema(fresh_db):
    """旧版数据库的 users 表没有 email 等列，初始化时应自动补齐"""
    Base.metadata.drop_all(bind=fresh_db)
    with fresh_db.begin() as conn:
        conn.execute(text(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, username VARCHAR(50) UNIQUE, "
            "password_hash VARCHAR(100), created_at DATETIME, last_login DATETIME)"
        ))
    init_db()
    columns = {column["name"] for column in inspect(fresh_db).get_columns("users")}
    assert {"email", "remember_token_hash"} <= columns
    assert UserService.create_user("alice", "secret123", "alice@example.com")
