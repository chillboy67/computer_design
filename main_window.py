'''
主页面代码 - 优化版
1. 增加输入验证
2. 集成数据存储功能
3. 优化代码结构

-- wy 2025-03-01
'''

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox,
    QFormLayout, QComboBox, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

from llm_utils import get_LLM_response
from ai_for_halthy import get_AI_response
from sport_page import SportPrescriptionPage
from health_page import HealthAssessmentPage
from fresh import LoadingScreen
from user_service import UserService

class MainWindow(QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user  # 当前登录用户
        self.init_ui()
        self.load_saved_data()  # 加载已保存数据

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("健康信息管理系统")
        self.resize(600, 800)  # 调整窗口尺寸

        # 主布局
        main_layout = QVBoxLayout(self)

        # 创建带滚动区域的输入表单
        scroll_area = self.create_input_form()
        main_layout.addWidget(scroll_area)

        # 底部操作按钮
        button_layout = self.create_action_buttons()
        main_layout.addLayout(button_layout)

    def create_input_form(self):
        """创建输入表单区域"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)

        # 基本信息组
        basic_group = QGroupBox("基本信息（必填）")
        basic_form = self.create_basic_info_form()
        basic_group.setLayout(basic_form)
        layout.addWidget(basic_group)

        # 临床数据组
        clinical_group = QGroupBox("临床数据（选填）")
        clinical_form = self.create_clinical_form()
        clinical_group.setLayout(clinical_form)
        layout.addWidget(clinical_group)

        scroll.setWidget(content)
        return scroll

    def create_basic_info_form(self):
        """创建基本信息表单"""
        form = QFormLayout()

        # 性别选择
        self.gender_input = QComboBox()
        self.gender_input.addItems(["男", "女", "其他"])
        form.addRow("性别:", self.gender_input)

        # 年龄输入（限制1-120）
        self.age_input = QLineEdit()
        self.age_input.setValidator(self.create_number_validator(1, 120))
        self.age_input.setPlaceholderText("1-120岁")
        form.addRow("年龄:", self.age_input)

        # 身高输入（限制50-250cm）
        self.height_input = QLineEdit()
        self.height_input.setValidator(self.create_number_validator(50, 250))
        self.height_input.setPlaceholderText("50-250厘米")
        form.addRow("身高:", self.height_input)

        # 体重输入（限制20-300kg）
        self.weight_input = QLineEdit()
        self.weight_input.setValidator(self.create_number_validator(20, 300))
        self.weight_input.setPlaceholderText("20-300公斤")
        form.addRow("体重:", self.weight_input)

        return form

    def create_clinical_form(self):
        """创建临床数据表单"""
        form = QFormLayout()

        # 血压组
        self.SBP_input = self.create_number_field("收缩压（高压）:", "90-180 mmHg")
        self.DBP_input = self.create_number_field("舒张压（低压）:", "60-120 mmHg")

        # 代谢指标
        self.glucose_input = self.create_number_field("空腹血糖:", "3.9-6.1 mmol/L")
        self.triglycerides_input = self.create_number_field("甘油三酯:", "0.56-1.7 mmol/L")

        # 体成分
        self.body_fat_input = self.create_number_field("体脂率:", "10-50%", 0, 50)
        self.waist_input = self.create_number_field("腰围:", "50-150厘米", 50, 150)

        return form

    def create_action_buttons(self):
        """创建底部操作按钮"""
        layout = QHBoxLayout()

        # 保存按钮
        self.save_button = QPushButton("保存数据")
        self.save_button.setMinimumHeight(40)
        self.save_button.clicked.connect(self.save_all_data)
        layout.addWidget(self.save_button)

        # 运动处方按钮
        self.sport_button = QPushButton("生成运动处方")
        self.sport_button.setMinimumHeight(40)
        self.sport_button.clicked.connect(self.open_sport_prescription)
        layout.addWidget(self.sport_button)

        # 健康评估按钮
        self.health_button = QPushButton("生成健康评估")
        self.health_button.setMinimumHeight(40)
        self.health_button.clicked.connect(self.open_health_assessment)
        layout.addWidget(self.health_button)

        return layout

    # --------------------------
    # 核心功能方法
    # --------------------------
    def create_number_validator(self, min_val, max_val):
        """创建数字输入验证器"""
        regex = QRegularExpression(f"^\\d+(\\.\\d+)?$")
        validator = QRegularExpressionValidator(regex, self)
        validator.setRange(min_val, max_val, 1)
        return validator

    def create_number_field(self, label, placeholder, min=0, max=999):
        """创建标准化数字输入字段"""
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setValidator(self.create_number_validator(min, max))
        self.clinical_form.addRow(label, field)
        return field

    def load_saved_data(self):
        """加载已保存的用户数据"""
        basic_info = UserService.get_basic_info(self.current_user)
        if basic_info:
            self.gender_input.setCurrentText(basic_info.get("gender", ""))
            self.age_input.setText(str(basic_info.get("age", "")))
            self.height_input.setText(str(basic_info.get("height", "")))
            self.weight_input.setText(str(basic_info.get("weight", "")))

    def validate_inputs(self):
        """验证必填字段"""
        required_fields = {
            "年龄": self.age_input,
            "身高": self.height_input,
            "体重": self.weight_input
        }

        for field_name, widget in required_fields.items():
            if not widget.text().strip():
                QMessageBox.warning(self, "缺失信息", f"{field_name}为必填项")
                widget.setFocus()
                return False
            try:
                float(widget.text())
            except ValueError:
                QMessageBox.warning(self, "输入错误", f"{field_name}必须为数字")
                widget.setFocus()
                return False
        return True

    def save_all_data(self):
        """保存所有数据到数据库"""
        if not self.validate_inputs():
            return

        # 收集基础数据
        basic_data = {
            "age": int(self.age_input.text()),
            "gender": self.gender_input.currentText(),
            "height": float(self.height_input.text()),
            "weight": float(self.weight_input.text())
        }

        # 保存基础信息
        if UserService.update_basic_info(self.current_user, **basic_data):
            QMessageBox.information(self, "成功", "基础信息已保存")
        else:
            QMessageBox.warning(self, "错误", "基础信息保存失败")

        # 收集临床数据
        clinical_data = {
            "sbp": self.SBP_input.text() or None,
            "dbp": self.DBP_input.text() or None,
            "glucose": self.glucose_input.text() or None,
            "triglycerides": self.triglycerides_input.text() or None,
            "body_fat": self.body_fat_input.text() or None,
            "waist": self.waist_input.text() or None
        }

        # 过滤有效临床数据
        valid_data = {k: float(v) for k, v in clinical_data.items() if v}
        if valid_data:
            if UserService.add_clinical_record(self.current_user, **valid_data):
                QMessageBox.information(self, "成功", "临床数据已保存")
            else:
                QMessageBox.warning(self, "错误", "临床数据保存失败")

    # --------------------------
    # AI功能模块
    # --------------------------
    def open_sport_prescription(self):
        """生成运动处方"""
        if not self.validate_inputs():
            return

        prompt = f"""...（同原逻辑，略）..."""

        self.loading_screen = LoadingScreen(self)
        self.loading_screen.start_loading(
            get_LLM_response,
            prompt,
            self.on_sport_response_ready
        )

    def open_health_assessment(self):
        """生成健康评估"""
        if not self.validate_inputs():
            return

        prompt = f"""...（同原逻辑，略）..."""

        self.loading_screen = LoadingScreen(self)
        self.loading_screen.start_loading(
            get_LLM_response,
            prompt,
            self.on_health_response_ready
        )

    # --------------------------
    # 响应处理方法
    # --------------------------
    def on_sport_response_ready(self, response):
        self.sport_window = SportPrescriptionPage(response)
        self.sport_window.show()

    def on_health_response_ready(self, response):
        self.health_window = HealthAssessmentPage(response)
        self.health_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(current_user="admin")  # 从登录模块传入实际用户名
    window.show()
    sys.exit(app.exec())