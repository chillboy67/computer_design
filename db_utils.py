# db_utils.py
import sqlite3
import bcrypt
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

DATABASE = 'health_db.sqlite'

# 加载环境变量
load_dotenv()

# 根据环境变量选择数据库
DATABASE_URL = os.getenv("DATABASE_URL")

# 配置 SQL 方言
if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
elif DATABASE_URL.startswith("mysql"):
    # MySQL
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
elif DATABASE_URL.startswith("sqlite"):
    # SQLite
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    raise ValueError("不支持的数据库类型")

# 创建 SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()

# 数据库上下文管理器
@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    Base.metadata.create_all(bind=engine)  # 数据库初始化
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS health_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                sbp INTEGER,
                dbp INTEGER,
                glucose REAL,
                triglycerides REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()