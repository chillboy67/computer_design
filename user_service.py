# user_service.py
import bcrypt
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from db_utils import SessionLocal
from models import User, HealthRecord
from datetime import datetime

class UserService:
    @staticmethod
    def create_user(username, password):
        """创建用户并返回布尔状态"""
        try:
            hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            with SessionLocal() as session:
                user = User(
                    username=username,
                    password_hash=hashed_pw,
                    created_at=datetime.now()
                )
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

    @staticmethod
    def update_last_login(username):
        """更新最后登录时间"""
        try:
            with SessionLocal() as session:
                user = session.query(User).filter(User.username == username).first()
                if user:
                    user.last_login = datetime.now()
                    session.commit()
        except SQLAlchemyError as e:
            print(f"更新登录时间失败: {str(e)}")

    @staticmethod
    def get_last_user():
        """获取最近登录的用户"""
        try:
            with SessionLocal() as session:
                return session.query(User).order_by(User.last_login.desc()).first()
        except SQLAlchemyError as e:
            print(f"查询最近用户失败: {str(e)}")
            return None

    @staticmethod
    def update_basic_info(username, age, gender, height, weight, contact, emergency_contact):
        """更新用户基础信息"""
        try:
            with SessionLocal() as session:
                user = session.query(User).filter(User.username == username).first()
                if user:
                    user.age = age
                    user.gender = gender
                    user.height = height
                    user.weight = weight
                    user.contact = contact
                    user.emergency_contact = emergency_contact
                    session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            print(f"更新基础信息失败: {str(e)}")
            return False

    @staticmethod
    def add_clinical_record(username, sbp, dbp, glucose, cholesterol, notes=None):
        """添加临床数据记录"""
        try:
            with SessionLocal() as session:
                user = session.query(User).filter(User.username == username).first()
                if user:
                    record = ClinicalRecord(
                        user_id=user.id,
                        sbp=sbp,
                        dbp=dbp,
                        glucose=glucose,
                        cholesterol=cholesterol,
                        notes=notes,
                        recorded_at=datetime.now()
                    )
                    session.add(record)
                    session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            print(f"添加临床记录失败: {str(e)}")
            return False

    @staticmethod
    def get_basic_info(username):
        """获取用户基础信息"""
        try:
            with SessionLocal() as session:
                user = session.query(User).filter(User.username == username).first()
                if user:
                    return {
                        "age": user.age,
                        "gender": user.gender,
                        "height": user.height,
                        "weight": user.weight,
                        "contact": user.contact,
                        "emergency_contact": user.emergency_contact
                    }
                return None
        except SQLAlchemyError as e:
            print(f"获取基础信息失败: {str(e)}")
            return None

    @staticmethod
    def get_clinical_records(username, limit=10):
        """获取用户最近的临床记录"""
        try:
            with SessionLocal() as session:
                user = session.query(User).filter(User.username == username).first()
                if user:
                    records = session.query(ClinicalRecord)\
                        .filter(ClinicalRecord.user_id == user.id)\
                        .order_by(ClinicalRecord.recorded_at.desc())\
                        .limit(limit)\
                        .all()
                    return [{
                        "recorded_at": r.recorded_at,
                        "sbp": r.sbp,
                        "dbp": r.dbp,
                        "glucose": r.glucose,
                        "cholesterol": r.cholesterol,
                        "notes": r.notes
                    } for r in records]
                return []
        except SQLAlchemyError as e:
            print(f"获取临床记录失败: {str(e)}")
            return []