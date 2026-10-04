import logging

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

import config
from base import Base

logger = logging.getLogger(__name__)

if config.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(config.DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _add_missing_columns():
    """create_all 不会修改已存在的表，这里为旧版本数据库补齐新增的列"""
    inspector = inspect(engine)
    for table in Base.metadata.sorted_tables:
        if not inspector.has_table(table.name):
            continue
        existing = {column["name"] for column in inspector.get_columns(table.name)}
        for column in table.columns:
            if column.name in existing:
                continue
            column_type = column.type.compile(dialect=engine.dialect)
            with engine.begin() as conn:
                conn.execute(text(f"ALTER TABLE {table.name} ADD COLUMN {column.name} {column_type}"))
            logger.info("已为表 %s 补充列 %s", table.name, column.name)


def init_db():
    """创建数据表，并按配置创建演示账号"""
    import models  # noqa: F401  注册模型到 Base.metadata
    from user_service import UserService

    Base.metadata.create_all(bind=engine)
    _add_missing_columns()

    username = config.DEFAULT_ADMIN_USERNAME
    password = config.DEFAULT_ADMIN_PASSWORD
    if username and password and not UserService.user_exists(username):
        UserService.create_user(username, password)
        logger.info("已创建演示账号 %s", username)
    logger.info("数据库初始化完成")
