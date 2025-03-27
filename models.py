# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from base import Base  # 从 base.py 导入 Base，而非 db_utils

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password_hash = Column(String(100))
    created_at = Column(DateTime)

class HealthRecord(Base):
    __tablename__ = "health_records"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    sbp = Column(Integer)
    dbp = Column(Integer)
    glucose = Column(Float)
    triglycerides = Column(Float)
    created_at = Column(DateTime)