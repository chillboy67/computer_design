# db_utils.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# 1. 加载环境变量
load_dotenv()

# 2. 设置默认数据库连接（防止环境变量未配置）
DATABASE_URL = os.getenv(
    "DATABASE_URL",  # 从 .env 文件中读取
    "sqlite:///health_db.sqlite"  # 默认值（SQLite）
)

# 3. 配置数据库引擎
if DATABASE_URL.startswith("sqlite"):
    # SQLite 需要特殊参数 `check_same_thread`
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # 其他数据库（如 PostgreSQL/MySQL）直接连接
    engine = create_engine(DATABASE_URL)

# 4. 创建数据库会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 5. 声明基类（用于 ORM 模型继承）
Base = declarative_base()

# 6. 初始化数据库（创建所有表）
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("[Success] Database initialized.")
    except Exception as e:
        print(f"[Error] Database initialization failed: {str(e)}")