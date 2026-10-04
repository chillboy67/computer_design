"""集中管理项目配置：路径、数据库、AI 服务等，敏感信息统一从 .env 读取"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# 静态资源
ASSETS_DIR = BASE_DIR / "assets"
LOGIN_IMAGE = ASSETS_DIR / "login.jpg"
LOADING_IMAGE = ASSETS_DIR / "loading.png"

# 数据库：默认放在项目目录下，避免从其他目录启动时找不到数据库
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'health_db.sqlite'}"

# AI 服务
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "glm-4-plus").strip() or "glm-4-plus"
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "60") or 60)

# 演示账号（密码为空则不创建）
DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin").strip()
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "")
