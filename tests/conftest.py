import os
import tempfile
from pathlib import Path

import pytest

# 必须在导入项目模块之前设置：使用独立的临时数据库和配置目录，界面测试不弹出窗口
_tmp = Path(tempfile.mkdtemp())
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp / 'test.db'}"
os.environ["DEFAULT_ADMIN_PASSWORD"] = ""
os.environ["LLM_API_KEY"] = ""
os.environ["ZHIPUAI_API_KEY"] = ""
os.environ["LLM_BASE_URL"] = ""
os.environ["XDG_CONFIG_HOME"] = str(_tmp / "config")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture
def fresh_db():
    from base import Base
    from db_utils import engine, init_db

    Base.metadata.drop_all(bind=engine)
    init_db()
    yield engine
