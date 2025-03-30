# models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from base import Base  # 确保导入Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password_hash = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)

# 确保 HealthRecord 类存在且拼写正确
class HealthRecord(Base):  # <-- 关键点：检查类名是否一致
    __tablename__ = "health_records"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    sbp = Column(Integer)    # 收缩压
    dbp = Column(Integer)    # 舒张压
    glucose = Column(Float)  # 血糖
    triglycerides = Column(Float)  # 甘油三酯
    created_at = Column(DateTime, default=datetime.now)