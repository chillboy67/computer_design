'''
主页面代码，实现用户健康信息的输入，并获取LLM的健康建议

-- wy 2025-02-26
'''

import sys
import markdown
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox
from PySide6.QtCore import Qt

from llm_utils import get_LLM_response
from sport_page import SportPrescriptionPage
from ai_for_health import get_AI_response
from fresh import LoadingScreen

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 创建主布局，水平布局（左边和右边）
        main_layout = QHBoxLayout()

        # 左边布局 - 健康信息输入
        left_layout = QVBoxLayout()
        self.SBP_input = QLineEdit()  # 高压
        self.DBP_input = QLineEdit()  # 低压
        self.glucose_input = QLineEdit()  # 血糖
        self.triglycerides_input = QLineEdit()  # 甘油三酯

        # 创建标签
        left_layout.addWidget(QLabel("健康信息"))
        left_layout.addWidget(QLabel("高压"))
        left_layout.addWidget(self.SBP_input)
        left_layout.addWidget(QLabel("低压"))
        left_layout.addWidget(self.DBP_input)
        left_layout.addWidget(QLabel("血糖"))
        left_layout.addWidget(self.glucose_input)
        left_layout.addWidget(QLabel("甘油三酯"))
        left_layout.addWidget(self.triglycerides_input)

        # 创建两个按钮
        self.sport_button = QPushButton("运动处方")
        self.sport_button.clicked.connect(self.on_sport_submit)
        left_layout.addWidget(self.sport_button)

        self.health_button = QPushButton("健康评估")
        self.health_button.clicked.connect(self.on_health_submit)
        left_layout.addWidget(self.health_button)

        # 右边布局 - 诊断结果
        self.diagnosis_output = QTextEdit()  # 用来显示诊断结果
        self.diagnosis_output.setPlaceholderText("等待用户输入...")
        self.diagnosis_output.setReadOnly(True)  # 设置为只读，避免用户修改
        self.diagnosis_output.setFixedWidth(580)  # 设置固定宽度为580

        # 将左边和右边布局加入主布局
        main_layout.addLayout(left_layout, 1)
        main_layout.addWidget(self.diagnosis_output, 2)

        # 设置主布局
        self.setLayout(main_layout)

        # 存储响应结果
        self.response = None

    def validate_inputs(self):
        """验证输入，允许部分输入为空"""
        values = {}
        fields = {
            'SBP': self.SBP_input.text(),
            'DBP': self.DBP_input.text(),
            'glucose': self.glucose_input.text(),
            'triglycerides': self.triglycerides_input.text()
        }

        # 检查是否所有字段都为空
        if all(not text for text in fields.values()):
            QMessageBox.warning(self, "输入缺失", "请至少输入一项健康指标。")
            return None

        # 处理每个输入，如果为空则使用None
        for key, text in fields.items():
            if not text:
                values[key] = None
            else:
                try:
                    values[key] = float(text)
                except ValueError:
                    QMessageBox.warning(self, "输入错误", f"{key} 必须是数字。")
                    return None

        return values

    def on_sport_submit(self):
        values = self.validate_inputs()
        if values is None:
            return

        # 构建根据可用数据的prompt
        prompt_parts = ['请为一位患者设计合理的运动建议，患者的健康指标如下：']

        if values['SBP'] is not None:
            prompt_parts.append(f"高压值是：{values['SBP']}")

        if values['DBP'] is not None:
            prompt_parts.append(f"低压值是：{values['DBP']}")

        if values['glucose'] is not None:
            prompt_parts.append(f"血糖是：{values['glucose']}")

        if values['triglycerides'] is not None:
            prompt_parts.append(f"甘油三酯是：{values['triglycerides']}")

        prompt_parts.append("\n请严格按以下格式组织回答：")
        prompt_parts.append("运动项目：（适合的运动类型）")
        prompt_parts.append("运动频率：（建议的运动频次）")
        prompt_parts.append("运动强度：（适宜的运动强度水平）")

        prompt = "。".join(prompt_parts)

        # 显示加载屏幕并执行AI请求
        loading_screen = LoadingScreen(self)

        def handle_response(response):
            self.response = response
            self.diagnosis_output.setPlaceholderText("已生成运动处方，请在新窗口查看详细内容")
            self.sport_prescription_window = SportPrescriptionPage(response)
            self.sport_prescription_window.show()

        loading_screen.start_loading(get_LLM_response, prompt, handle_response)

    def on_health_submit(self):
        values = self.validate_inputs()
        if values is None:
            return

        # 构建根据可用数据的prompt
        prompt_parts = ['请对一位患者的健康状况进行评估，患者的健康指标如下：']

        if values['SBP'] is not None:
            prompt_parts.append(f"高压值是：{values['SBP']}")

        if values['DBP'] is not None:
            prompt_parts.append(f"低压值是：{values['DBP']}")

        if values['glucose'] is not None:
            prompt_parts.append(f"血糖是：{values['glucose']}")

        if values['triglycerides'] is not None:
            prompt_parts.append(f"甘油三酯是：{values['triglycerides']}")

        prompt = "。".join(prompt_parts)

        # 显示加载屏幕并执行AI请求
        loading_screen = LoadingScreen(self)

        def handle_response(response):
            html_response = markdown.markdown(response)
            self.diagnosis_output.setHtml(html_response)

        loading_screen.start_loading(get_AI_response, prompt, handle_response)