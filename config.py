"""集中管理项目配置：路径、数据库、AI 服务等，敏感信息统一从 .env 读取"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

if getattr(sys, "frozen", False):
    # PyInstaller 打包后：图片等资源在程序自带的目录中，.env 和数据库放在 exe 所在目录
    APP_DIR = Path(sys.executable).resolve().parent
    RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", APP_DIR))
else:
    APP_DIR = RESOURCE_DIR = Path(__file__).resolve().parent

load_dotenv(APP_DIR / ".env")

# 静态资源
ASSETS_DIR = RESOURCE_DIR / "assets"
LOGIN_IMAGE = ASSETS_DIR / "login.jpg"
LOADING_IMAGE = ASSETS_DIR / "loading.jpg"
APP_ICON = ASSETS_DIR / "app.ico"

# 数据库：默认放在程序目录下，避免从其他目录启动时找不到数据库
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{APP_DIR / 'health_db.sqlite'}"

# AI 服务：默认使用智谱 AI；填写 LLM_BASE_URL 后可换成其他兼容 OpenAI 接口格式的服务
LLM_API_KEY = (os.getenv("LLM_API_KEY") or os.getenv("ZHIPUAI_API_KEY") or "").strip()  # 兼容旧配置名
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "").strip() or None  # 为空时使用智谱 AI 的接口地址
LLM_MODEL = os.getenv("LLM_MODEL", "glm-4-plus").strip() or "glm-4-plus"
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "60") or 60)

# 演示账号（密码为空则不创建）
DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin").strip()
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "")
