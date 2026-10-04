from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from base import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120))
    password_hash = Column(String(100), nullable=False)  # bcrypt 哈希
    remember_token_hash = Column(String(64))  # “记住密码”令牌的 SHA-256，不保存明文密码
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)


class HealthRecord(Base):
    __tablename__ = "health_records"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    sbp = Column(Integer)
    dbp = Column(Integer)
    glucose = Column(Float)
    triglycerides = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
