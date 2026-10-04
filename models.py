from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

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
    """一次健康评估或运动处方：保存当时填写的数据和生成的报告"""
    __tablename__ = "health_records"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    record_type = Column(String(10))  # health：健康评估，sport：运动处方
    gender = Column(String(4))
    # 以下字段名与 prompts.py 中的 Field.key 一致
    age = Column(Integer)
    height = Column(Float)
    weight = Column(Float)
    bmi = Column(Float)
    body_fat = Column(Float)
    muscle_mass = Column(Float)
    waist = Column(Float)
    sbp = Column(Integer)
    dbp = Column(Integer)
    heart_rate = Column(Integer)
    glucose = Column(Float)
    triglycerides = Column(Float)
    report_text = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
