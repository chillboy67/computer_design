# db_utils.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from base import Base  # 从 base.py 导入 Base

load_dotenv()

# 配置数据库连接
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///health_db.sqlite")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        from models import User, HealthRecord  # 延迟导入
        print("正在创建数据库表...")
        Base.metadata.create_all(bind=engine)
        print("表结构创建成功")

        # 创建默认用户
        from user_service import UserService
        if not UserService.verify_user("admin", "123"):
            print("正在创建默认用户 admin...")
            UserService.create_user("admin", "123")
        else:
            print("默认用户已存在")
    except Exception as e:
        print(f"[Critical Error] 初始化失败: {str(e)}")
        raise  # 抛出异常以终止程序