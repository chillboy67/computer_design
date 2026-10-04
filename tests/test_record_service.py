from datetime import datetime, timedelta

from db_utils import SessionLocal
from models import HealthRecord
from record_service import RecordService, record_to_data, trend_points
from user_service import UserService

DATA = {"gender": "女", "age": 30.0, "height": 160.0, "weight": 55.5, "sbp": 118.4, "dbp": 76.0, "glucose": 5.2}


def test_save_and_list_records(fresh_db):
    UserService.create_user("alice", "secret123")
    first = RecordService.save_record("alice", "health", DATA, "## 心血管健康\n正常")
    second = RecordService.save_record("alice", "sport", {**DATA, "weight": 54.0}, "## 运动项目\n快走")
    assert first and second

    records = RecordService.list_records("alice")
    assert [r.id for r in records] == [second, first]  # 最新的在前
    record = records[1]
    assert record.record_type == "health"
    assert record.gender == "女"
    assert record.sbp == 118  # 整数字段四舍五入
    assert record.bmi == 21.7
    assert record.muscle_mass is None
    assert record.report_text.startswith("## 心血管健康")
    assert RecordService.latest_record("alice").id == second


def test_records_are_isolated_between_users(fresh_db):
    UserService.create_user("alice", "secret123")
    UserService.create_user("bob", "secret123")
    record_id = RecordService.save_record("alice", "health", DATA, "报告")
    assert RecordService.list_records("bob") == []
    assert RecordService.latest_record("bob") is None
    assert not RecordService.delete_record("bob", record_id)
    assert RecordService.delete_record("alice", record_id)
    assert RecordService.list_records("alice") == []


def test_save_for_unknown_user(fresh_db):
    assert RecordService.save_record("nobody", "health", DATA, "报告") is None


def test_record_to_data(fresh_db):
    UserService.create_user("alice", "secret123")
    RecordService.save_record("alice", "health", DATA, "报告")
    data = record_to_data(RecordService.latest_record("alice"))
    assert data["gender"] == "女"
    assert data["weight"] == 55.5
    assert data["heart_rate"] is None


def test_trend_points_sorted_and_skip_missing():
    now = datetime(2026, 1, 10)
    records = [
        HealthRecord(created_at=now, weight=60.0),
        HealthRecord(created_at=now - timedelta(days=2), weight=None),
        HealthRecord(created_at=now - timedelta(days=5), weight=62.0),
    ]
    assert trend_points(records, "weight") == [(now - timedelta(days=5), 62.0), (now, 60.0)]


def test_old_health_records_table_is_upgraded(fresh_db):
    """旧版 health_records 只有几列，初始化后应能正常保存完整记录"""
    from sqlalchemy import inspect, text
    from base import Base
    from db_utils import init_db

    Base.metadata.drop_all(bind=fresh_db)
    with fresh_db.begin() as conn:
        conn.execute(text(
            "CREATE TABLE health_records (id INTEGER PRIMARY KEY, user_id INTEGER, sbp INTEGER, "
            "dbp INTEGER, glucose FLOAT, triglycerides FLOAT, created_at DATETIME)"
        ))
    init_db()
    columns = {c["name"] for c in inspect(fresh_db).get_columns("health_records")}
    assert {"record_type", "weight", "report_text"} <= columns
    UserService.create_user("alice", "secret123")
    assert RecordService.save_record("alice", "health", DATA, "报告")
    with SessionLocal() as session:
        assert session.query(HealthRecord).count() == 1
