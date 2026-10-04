from PySide6.QtCore import QLocale
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (QComboBox, QFormLayout, QGroupBox, QHBoxLayout,
                               QLabel, QLineEdit, QMessageBox, QPushButton,
                               QScrollArea, QVBoxLayout, QWidget)

from fresh import LoadingScreen
from health_page import HealthAssessmentPage
from llm_utils import get_health_assessment, get_sport_prescription
from prompts import (BASIC_FIELDS, CLINICAL_FIELDS, build_health_prompt,
                     build_sport_prompt, check_consistency, parse_field)
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

        main_layout = QVBoxLayout(self)

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

    def _generate_report(self, ai_function, prompt, page_class):
        loading_screen = LoadingScreen(self)
        loading_screen.start_loading(ai_function, prompt, lambda response: self._show_report(page_class, response))
        loading_screen.deleteLater()

    def _show_report(self, page_class, response):
        window = page_class(response)
        self.report_windows = [w for w in self.report_windows if w.isVisible()]
        self.report_windows.append(window)
        window.show()

    def open_sport_prescription(self):
        """生成并打开运动处方页面"""
        data = self.get_user_data()
        if data:
            self._generate_report(get_sport_prescription, build_sport_prompt(data), SportPrescriptionPage)

    def open_health_assessment(self):
        """生成并打开健康评估页面"""
        data = self.get_user_data()
        if data:
            self._generate_report(get_health_assessment, build_health_prompt(data), HealthAssessmentPage)
