"""健康记录：保存每次评估的数据和报告，供历史记录和趋势图使用"""
import logging
from typing import Dict, List, Optional, Tuple

from sqlalchemy.exc import SQLAlchemyError

from db_utils import SessionLocal
from models import HealthRecord, User
from prompts import BASIC_FIELDS, CLINICAL_FIELDS, calc_bmi

logger = logging.getLogger(__name__)

RECORD_TYPES = {"health": "健康评估", "sport": "运动处方"}
FIELDS = BASIC_FIELDS + CLINICAL_FIELDS


def _user_id(session, username):
    user = session.query(User).filter(User.username == username).first()
    return user.id if user else None


def _user_records(session, username):
    return (
        session.query(HealthRecord)
        .join(User, HealthRecord.user_id == User.id)
        .filter(User.username == username)
    )


def record_to_data(record: HealthRecord) -> Dict:
    """把记录转换回输入数据的格式，用于“载入上次数据”"""
    data = {"gender": record.gender}
    for field in FIELDS:
        data[field.key] = getattr(record, field.key)
    return data


def trend_points(records, key) -> List[Tuple]:
    """取出某个指标的 (时间, 数值) 序列，按时间从早到晚排列，跳过未填写的记录"""
    points = [(r.created_at, getattr(r, key)) for r in records if getattr(r, key) is not None]
    return sorted(points, key=lambda point: point[0])


class RecordService:
    @staticmethod
    def save_record(username, record_type, data, report_text) -> Optional[int]:
        """保存一条记录，返回记录 id；用户不存在或出错时返回 None"""
        values = {}
        for field in FIELDS:
            value = data.get(field.key)
            if value is not None and field.decimals == 0:
                value = int(round(value))
            values[field.key] = value
        try:
            with SessionLocal() as session:
                user_id = _user_id(session, username)
                if user_id is None:
                    return None
                record = HealthRecord(
                    user_id=user_id,
                    record_type=record_type,
                    gender=data.get("gender"),
                    bmi=calc_bmi(data.get("height"), data.get("weight")),
                    report_text=report_text,
                    **values,
                )
                session.add(record)
                session.commit()
                return record.id
        except SQLAlchemyError:
            logger.exception("保存健康记录失败")
            return None

    @staticmethod
    def list_records(username) -> List[HealthRecord]:
        """某个用户的全部记录，最新的在前"""
        try:
            with SessionLocal() as session:
                return (
                    _user_records(session, username)
                    .order_by(HealthRecord.created_at.desc(), HealthRecord.id.desc())
                    .all()
                )
        except SQLAlchemyError:
            logger.exception("查询健康记录失败")
            return []

    @staticmethod
    def latest_record(username) -> Optional[HealthRecord]:
        try:
            with SessionLocal() as session:
                return (
                    _user_records(session, username)
                    .order_by(HealthRecord.created_at.desc(), HealthRecord.id.desc())
                    .first()
                )
        except SQLAlchemyError:
            logger.exception("查询健康记录失败")
            return None

    @staticmethod
    def delete_record(username, record_id) -> bool:
        """删除记录，只能删除属于该用户的记录"""
        try:
            with SessionLocal() as session:
                record = _user_records(session, username).filter(HealthRecord.id == record_id).first()
                if not record:
                    return False
                session.delete(record)
                session.commit()
                return True
        except SQLAlchemyError:
            logger.exception("删除健康记录失败")
            return False
