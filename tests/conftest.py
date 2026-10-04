import os
import tempfile
from pathlib import Path

import pytest

# 必须在导入项目模块之前设置，使测试使用独立的临时数据库
os.environ["DATABASE_URL"] = f"sqlite:///{Path(tempfile.mkdtemp()) / 'test.db'}"
os.environ["DEFAULT_ADMIN_PASSWORD"] = ""


@pytest.fixture
def fresh_db():
    from base import Base
    from db_utils import engine, init_db

    Base.metadata.drop_all(bind=engine)
    init_db()
    yield engine
