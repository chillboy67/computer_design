"""界面流程测试（无界面模式运行），AI 调用用假的流式函数代替"""
import time

import pytest

pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)

from PySide6.QtCore import QSettings  # noqa: E402
from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

import main_window as main_window_module  # noqa: E402
from history_page import HistoryPage  # noqa: E402
from llm_utils import LLMError  # noqa: E402
from login03 import SAVED_PASSWORD_PLACEHOLDER, MedicalLoginUI  # noqa: E402
from main_window import MainWindow  # noqa: E402
from record_service import RecordService  # noqa: E402
from user_service import UserService  # noqa: E402

REPORT = """根据您的数据，评估如下：

## 心血管健康
血压 135/88 mmHg，属于正常高值。

## 糖脂代谢
| 指标 | 数值 | 结论 |
|---|---|---|
| 空腹血糖 | 6.4 mmol/L | 空腹血糖受损 |

## 体成分
BMI 22.9 kg/m²，正常。
"""


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def messages(monkeypatch):
    """记录弹窗内容，代替真正弹出对话框"""
    shown = []

    def record(kind):
        def show(parent, title, text, *args, **kwargs):
            shown.append((kind, title, text))
            return QMessageBox.Yes
        return staticmethod(show)

    monkeypatch.setattr(QMessageBox, "information", record("info"))
    monkeypatch.setattr(QMessageBox, "warning", record("warn"))
    monkeypatch.setattr(QMessageBox, "question", record("question"))
    return shown


@pytest.fixture
def settings():
    s = QSettings("HealthApp", "Login")
    s.clear()
    yield s
    s.clear()


def wait_until(qapp, predicate, timeout=5.0):
    deadline = time.monotonic() + timeout
    while not predicate():
        if time.monotonic() > deadline:
            raise AssertionError("等待超时")
        qapp.processEvents()
        time.sleep(0.01)


def fake_stream(text, delay=0.01, chunk=8):
    def stream(prompt):
        assert "BMI：22.9" in prompt
        for i in range(0, len(text), chunk):
            time.sleep(delay)
            yield text[i:i + chunk]
    return stream


def make_main_window(qapp):
    window = MainWindow(username="alice")
    values = {"age": "30", "height": "175", "weight": "70", "sbp": "135", "dbp": "88",
              "heart_rate": "78", "glucose": "6.4", "triglycerides": "1.9"}
    for key, value in values.items():
        window.inputs[key].setText(value)
    window.show()
    return window


@pytest.fixture
def user(fresh_db):
    UserService.create_user("alice", "secret123")
    return "alice"


def test_register_login_and_remember(qapp, fresh_db, messages, settings):
    settings.setValue("password", "legacy-plain")  # 旧版本残留的明文密码
    login = MedicalLoginUI(MainWindow)
    assert settings.value("password") is None

    login.show_register_page()
    login.reg_username_input.setText("张三")
    login.reg_password_input.setText("secret123")
    login.reg_confirm_input.setText("secret12")
    login.register_user()
    assert messages[-1][2] == "两次输入的密码不一致"
    login.reg_confirm_input.setText("secret123")
    login.register_user()
    assert messages[-1][1] == "注册成功"
    assert login.username_input.text() == "张三"

    login.password_input.setText("wrong-pass")
    login.check_credentials()
    assert messages[-1][2] == "用户名或密码错误"

    login.password_input.setText("secret123")
    login.remember_me.setChecked(True)
    login.check_credentials()
    assert messages[-1][1] == "登录成功"
    assert "张三" in login.main_window_instance.windowTitle()
    assert settings.value("remember_token") and settings.value("password") is None

    # 再次打开时使用令牌登录
    again = MedicalLoginUI(MainWindow)
    assert again.password_input.text() == SAVED_PASSWORD_PLACEHOLDER
    again.remember_me.setChecked(False)
    again.check_credentials()
    assert messages[-1][1] == "登录成功"
    third = MedicalLoginUI(MainWindow)
    assert third.username_input.text() == "" and third.password_input.text() == ""


def test_input_validation(qapp, user, messages):
    window = MainWindow(username=user)
    window.open_health_assessment()
    assert messages[-1][2] == "请填写年龄"
    for key, value in {"age": "30", "height": "175", "weight": "70", "sbp": "80", "dbp": "120"}.items():
        window.inputs[key].setText(value)
    window.open_health_assessment()
    assert "收缩压应高于舒张压" in messages[-1][2]


def test_missing_api_key_shows_error(qapp, user, messages):
    window = make_main_window(qapp)
    window.open_health_assessment()
    assert messages[-1][1] == "生成失败" and "LLM_API_KEY" in messages[-1][2]
    assert window.report_windows == []


def test_streaming_report_is_saved(qapp, user, messages, monkeypatch):
    monkeypatch.setattr(main_window_module, "stream_health_assessment", fake_stream(REPORT, delay=0.05))
    window = make_main_window(qapp)
    window.open_health_assessment()

    page = window.report_windows[-1]
    assert page.worker is not None and page.stop_btn.isVisible()
    assert not page.nav_buttons[0].isEnabled()  # 生成过程中不能切换分节
    wait_until(qapp, lambda: page.worker is None)

    assert page.report_text == REPORT
    assert set(page.section_texts) == {"心血管健康", "糖脂代谢", "体成分"}
    assert page.nav_buttons[0].isEnabled() and not page.stop_btn.isVisible()
    assert page.status_label.text() == "生成完成"

    records = RecordService.list_records(user)
    assert len(records) == 1
    assert records[0].record_type == "health" and records[0].report_text == REPORT
    assert records[0].sbp == 135 and records[0].bmi == 22.9


def test_stream_failure_keeps_partial_report(qapp, user, messages, monkeypatch):
    def broken_stream(prompt):
        yield "## 运动项目\n快走"
        time.sleep(0.05)
        raise LLMError("网络中断")

    monkeypatch.setattr(main_window_module, "stream_sport_prescription", broken_stream)
    window = make_main_window(qapp)
    window.open_sport_prescription()  # 失败发生在加载窗口关闭之前，报告页也应展示已生成的部分
    page = window.report_windows[-1]
    wait_until(qapp, lambda: page.worker is None)

    assert messages[-1] == ("warn", "生成失败", "网络中断")
    assert page.report_text.startswith("## 运动项目")
    assert "中断" in page.status_label.text()
    assert RecordService.list_records(user) == []


def test_stop_generation(qapp, user, messages, monkeypatch):
    monkeypatch.setattr(main_window_module, "stream_health_assessment",
                        fake_stream(REPORT * 20, delay=0.05, chunk=4))
    window = make_main_window(qapp)
    window.open_health_assessment()
    page = window.report_windows[-1]
    page.stop_generation()

    assert page.worker is None and "已停止" in page.status_label.text()
    time.sleep(0.2)
    qapp.processEvents()
    assert RecordService.list_records(user) == []


def test_error_before_output_does_not_open_page(qapp, user, messages, monkeypatch):
    def failing_stream(prompt):
        raise LLMError("网络超时")
        yield  # noqa: unreachable，使其成为生成器

    monkeypatch.setattr(main_window_module, "stream_health_assessment", failing_stream)
    window = make_main_window(qapp)
    window.open_health_assessment()
    assert messages[-1] == ("warn", "生成失败", "网络超时")
    assert window.report_windows == []


def test_history_page_and_load_last_record(qapp, user, messages, monkeypatch):
    data = {"gender": "女", "age": 30, "height": 160, "weight": 58, "sbp": 128, "dbp": 82}
    RecordService.save_record(user, "health", data, REPORT)
    RecordService.save_record(user, "sport", {**data, "weight": 57}, "## 运动项目\n快走")

    window = MainWindow(username=user)
    window.load_last_record()
    assert window.gender_input.currentText() == "女"
    assert window.inputs["weight"].text() == "57"
    assert window.inputs["glucose"].text() == ""

    history = HistoryPage(user)
    assert history.table.rowCount() == 2
    assert history.table.item(0, 1).text() == "运动处方"
    assert history.table.item(1, 4).text() == "128/82"

    history.metric_combo.setCurrentText("体重")
    weight_series = [s for s in history.chart_view.chart().series() if s.name() == "体重"]
    assert weight_series and weight_series[0].count() == 2
    history.metric_combo.setCurrentText("空腹血糖")
    assert "暂无" in history.chart_view.chart().title()

    history.table.selectRow(1)
    history.view_report()
    report = history.report_windows[-1]
    assert report.report_text == REPORT and set(report.section_texts) == {"心血管健康", "糖脂代谢", "体成分"}

    history.table.selectRow(0)
    history.delete_record()
    assert messages[-1][0] == "question"
    assert history.table.rowCount() == 1
    assert len(RecordService.list_records(user)) == 1


def test_fast_stream_finishes_before_page_opens(qapp, user, messages, monkeypatch):
    """生成在加载窗口关闭前就已结束时，报告页仍能拿到完整结果并保存记录"""
    monkeypatch.setattr(main_window_module, "stream_health_assessment", fake_stream(REPORT, delay=0))
    window = make_main_window(qapp)
    window.open_health_assessment()
    page = window.report_windows[-1]
    wait_until(qapp, lambda: page.worker is None)
    assert page.report_text == REPORT
    assert len(RecordService.list_records(user)) == 1
