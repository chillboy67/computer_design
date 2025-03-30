from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime  # 新增导入
from base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password_hash = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime)
    last_login = Column(DateTime)  # 新增最后登录时间字段

class HealthRecord(Base):
    __tablename__ = "health_records"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    sbp = Column(Integer)
    dbp = Column(Integer)
    glucose = Column(Float)
    triglycerides = Column(Float)
    created_at = Column(DateTime)