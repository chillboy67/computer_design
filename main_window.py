from PySide6.QtCore import QLocale
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (QComboBox, QFormLayout, QGroupBox, QHBoxLayout,
                               QLabel, QLineEdit, QMessageBox, QPushButton,
                               QScrollArea, QVBoxLayout, QWidget)

from fresh import LoadingScreen, StreamWorker
from health_page import HealthAssessmentPage
from history_page import HistoryPage
from llm_utils import stream_health_assessment, stream_sport_prescription
from prompts import (BASIC_FIELDS, CLINICAL_FIELDS, build_health_prompt,
                     build_sport_prompt, check_consistency, format_number,
                     parse_field)
from record_service import RecordService, record_to_data
from report_page import DISCLAIMER
from sport_page import SportPrescriptionPage


class MainWindow(QWidget):
    def __init__(self, username=None):
        super().__init__()
        self.username = username
        self.setWindowTitle(f"健康信息输入 - {username}" if username else "健康信息输入")
        self.resize(500, 700)

        self.inputs = {}  # 字段 key -> 输入框
        self.report_windows = []  # 保持已打开报告窗口的引用，可同时查看多份报告
        self.history_window = None

        main_layout = QVBoxLayout(self)

        # 顶部：历史数据相关操作（需要登录）
        if username:
            top_layout = QHBoxLayout()
            load_button = QPushButton("载入上次数据")
            load_button.clicked.connect(self.load_last_record)
            history_button = QPushButton("历史记录与趋势")
            history_button.clicked.connect(self.open_history)
            top_layout.addWidget(load_button)
            top_layout.addStretch()
            top_layout.addWidget(history_button)
            main_layout.addLayout(top_layout)

        # 创建滚动区域以容纳所有输入字段
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # 基本信息组
        basic_group = QGroupBox("基本信息（必填）")
        basic_form = QFormLayout()
        self.gender_input = QComboBox()
        self.gender_input.addItems(["男", "女"])
        basic_form.addRow("性别:", self.gender_input)
        self._add_fields(basic_form, BASIC_FIELDS)
        basic_group.setLayout(basic_form)
        scroll_layout.addWidget(basic_group)

        # 临床数据组
        clinical_group = QGroupBox("临床数据（选填，填写越完整评估越准确）")
        clinical_form = QFormLayout()
        self._add_fields(clinical_form, CLINICAL_FIELDS)
        clinical_group.setLayout(clinical_form)
        scroll_layout.addWidget(clinical_group)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        disclaimer = QLabel(DISCLAIMER)
        disclaimer.setStyleSheet("color: #888888;")
        disclaimer.setWordWrap(True)
        main_layout.addWidget(disclaimer)

        # 底部按钮区域
        button_layout = QHBoxLayout()

        self.sport_button = QPushButton("运动处方")
        self.sport_button.setMinimumHeight(40)
        self.sport_button.clicked.connect(self.open_sport_prescription)
        button_layout.addWidget(self.sport_button)

        self.health_button = QPushButton("健康评估")
        self.health_button.setMinimumHeight(40)
        self.health_button.clicked.connect(self.open_health_assessment)
        button_layout.addWidget(self.health_button)

        main_layout.addLayout(button_layout)

    def _add_fields(self, form, fields):
        for field in fields:
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(field.unit)
            validator = QDoubleValidator(0, field.maximum, field.decimals, line_edit)
            validator.setNotation(QDoubleValidator.StandardNotation)
            validator.setLocale(QLocale.c())  # 统一使用小数点作为小数分隔符
            line_edit.setValidator(validator)
            form.addRow(f"{field.label}:", line_edit)
            self.inputs[field.key] = line_edit

    def get_user_data(self):
        """收集并校验用户输入的健康数据，数据不合法时弹窗提示并返回 None"""
        data = {"gender": self.gender_input.currentText()}
        try:
            for field in BASIC_FIELDS + CLINICAL_FIELDS:
                try:
                    data[field.key] = parse_field(field, self.inputs[field.key].text())
                except ValueError:
                    self.inputs[field.key].setFocus()
                    raise
            check_consistency(data)
        except ValueError as e:
            QMessageBox.warning(self, "输入有误", str(e))
            return None
        return data

    def _generate_report(self, record_type, page_class, stream_function, prompt, data):
        """等待 AI 开始输出后打开报告页，报告页中实时显示生成过程，完成后保存记录"""
        worker = StreamWorker(stream_function, prompt)
        loading_screen = LoadingScreen(self)
        started = loading_screen.wait_for_output(worker)
        loading_screen.deleteLater()
        if not started:
            return
        window = page_class()
        window.generation_finished.connect(lambda text: self._save_record(record_type, data, text))
        window.attach_stream(worker)
        self.report_windows = [w for w in self.report_windows if w.isVisible()]
        self.report_windows.append(window)
        window.show()

    def _save_record(self, record_type, data, report_text):
        if not self.username:
            return
        if RecordService.save_record(self.username, record_type, data, report_text) is None:
            QMessageBox.warning(self, "提示", "报告已生成，但保存到历史记录失败")
        elif self.history_window and self.history_window.isVisible():
            self.history_window.reload()

    def open_sport_prescription(self):
        """生成并打开运动处方页面"""
        data = self.get_user_data()
        if data:
            self._generate_report("sport", SportPrescriptionPage, stream_sport_prescription,
                                  build_sport_prompt(data), data)

    def open_health_assessment(self):
        """生成并打开健康评估页面"""
        data = self.get_user_data()
        if data:
            self._generate_report("health", HealthAssessmentPage, stream_health_assessment,
                                  build_health_prompt(data), data)

    def open_history(self):
        if self.history_window is None:
            self.history_window = HistoryPage(self.username)
        else:
            self.history_window.reload()
        self.history_window.show()
        self.history_window.raise_()
        self.history_window.activateWindow()

    def load_last_record(self):
        """用最近一次记录填充输入框，方便在上次的基础上修改"""
        record = RecordService.latest_record(self.username)
        if not record:
            QMessageBox.information(self, "提示", "暂无历史记录")
            return
        data = record_to_data(record)
        if data.get("gender"):
            self.gender_input.setCurrentText(data["gender"])
        for key, line_edit in self.inputs.items():
            value = data.get(key)
            line_edit.setText("" if value is None else format_number(value))
