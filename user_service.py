import hashlib
import hmac
import logging
import re
import secrets
from datetime import datetime
from typing import Optional

import bcrypt
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db_utils import SessionLocal
from models import User

logger = logging.getLogger(__name__)

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_\u4e00-\u9fa5]{2,20}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 6


def _hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


def _find_user(session, username):
    return session.query(User).filter(User.username == username).first()


class UserService:
    @staticmethod
    def validate_registration(username, email, password) -> Optional[str]:
        """校验注册信息，返回错误提示；校验通过时返回 None"""
        if not USERNAME_PATTERN.match(username):
            return "用户名需为 2-20 位字母、数字、下划线或汉字"
        if email and not EMAIL_PATTERN.match(email):
            return "邮箱格式不正确"
        if len(password) < MIN_PASSWORD_LENGTH:
            return f"密码长度至少为 {MIN_PASSWORD_LENGTH} 位"
        return None

    @staticmethod
    def create_user(username, password, email=None) -> bool:
        """创建用户，用户名已存在或数据库出错时返回 False"""
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        try:
            with SessionLocal() as session:
                session.add(User(username=username, email=email or None, password_hash=hashed_pw))
                session.commit()
            return True
        except IntegrityError:
            logger.info("用户名 %s 已存在", username)
            return False
        except SQLAlchemyError:
            logger.exception("创建用户失败")
            return False

    @staticmethod
    def user_exists(username) -> bool:
        with SessionLocal() as session:
            return _find_user(session, username) is not None

    @staticmethod
    def verify_user(username, password) -> bool:
        """验证用户名和密码"""
        try:
            with SessionLocal() as session:
                user = _find_user(session, username)
        except SQLAlchemyError:
            logger.exception("验证用户时发生错误")
            return False
        if not user or not user.password_hash:
            return False
        stored = user.password_hash
        if isinstance(stored, str):  # 旧版本以 bytes 形式存储，这里两种都兼容
            stored = stored.encode()
        try:
            return bcrypt.checkpw(password.encode(), stored)
        except ValueError:  # 非 bcrypt 格式的历史数据
            return False

    @staticmethod
    def update_last_login(username):
        try:
            with SessionLocal() as session:
                user = _find_user(session, username)
                if user:
                    user.last_login = datetime.now()
                    session.commit()
        except SQLAlchemyError:
            logger.exception("更新登录时间失败")

    @staticmethod
    def issue_remember_token(username) -> Optional[str]:
        """生成“记住密码”令牌：本地只保存随机令牌，数据库只保存令牌哈希"""
        token = secrets.token_urlsafe(32)
        try:
            with SessionLocal() as session:
                user = _find_user(session, username)
                if not user:
                    return None
                user.remember_token_hash = _hash_token(token)
                session.commit()
            return token
        except SQLAlchemyError:
            logger.exception("保存登录令牌失败")
            return None

    @staticmethod
    def verify_remember_token(username, token) -> bool:
        if not token:
            return False
        try:
            with SessionLocal() as session:
                user = _find_user(session, username)
        except SQLAlchemyError:
            logger.exception("验证登录令牌时发生错误")
            return False
        if not user or not user.remember_token_hash:
            return False
        return hmac.compare_digest(user.remember_token_hash, _hash_token(token))

    @staticmethod
    def clear_remember_token(username):
        try:
            with SessionLocal() as session:
                user = _find_user(session, username)
                if user and user.remember_token_hash:
                    user.remember_token_hash = None
                    session.commit()
        except SQLAlchemyError:
            logger.exception("清除登录令牌失败")
