# user_service.py
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from db_utils import SessionLocal
from models import User, HealthRecord
import bcrypt

class UserService:
    @staticmethod
    def create_user(username, password):
        """创建用户并返回布尔状态"""
        try:
            hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            with SessionLocal() as session:
                user = User(username=username, password_hash=hashed_pw)
                session.add(user)
                session.commit()
                return True
        except IntegrityError:
            print(f"用户名 {username} 已存在")
            session.rollback()
            return False
        except SQLAlchemyError as e:
            print(f"数据库操作失败: {str(e)}")
            session.rollback()
            return False

    @staticmethod
    def verify_user(username, password):
        """验证用户凭据"""
        try:
            with SessionLocal() as session:
                user = session.query(User).filter(User.username == username).first()
                if user and bcrypt.checkpw(password.encode(), user.password_hash):
                    return True
                return False
        except SQLAlchemyError as e:
            print(f"验证用户时发生错误: {str(e)}")
            return False