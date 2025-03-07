'''
主页面代码，实现用户健康信息的输入，并获取LLM的健康建议

-- wy 2025-02-26
'''

import sys
import markdown
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from PySide6.QtCore import Qt

from llm_utils import get_LLM_response
from sport_page import SportPrescriptionPage
from ai_for_health import get_AI_response

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

        # 提交按钮
        self.submit_button = QPushButton("提交")
        self.submit_button.clicked.connect(self.on_submit)
        left_layout.addWidget(self.submit_button)

        # 右边布局 - 诊断结果
        self.diagnosis_output = QTextEdit()  # 用来显示诊断结果
        self.diagnosis_output.setPlaceholderText("等待用户输入...")
        self.diagnosis_output.setReadOnly(True)  # 设置为只读，避免用户修改
        self.diagnosis_output.setFixedWidth(580)  # 设置固定宽度为400

        # 运动处方按钮
        self.sport_prescription_button = QPushButton("运动处方")
        self.sport_prescription_button.clicked.connect(self.open_sport_prescription_page)
        self.sport_prescription_button.setEnabled(False)  # 初始状态下禁用按钮
        left_layout.addWidget(self.sport_prescription_button)

        # 将左边和右边布局加入主布局
        main_layout.addLayout(left_layout, 1)
        main_layout.addWidget(self.diagnosis_output, 2)

        # 设置主布局
        self.setLayout(main_layout)

    def on_submit(self):
        # 获取用户输入的数据
        SBP = self.SBP_input.text()
        DBP = self.DBP_input.text()
        glucose = self.glucose_input.text()
        triglycerides = self.triglycerides_input.text()

        # 构建 prompt，获取 LLM 的输出
        prompt = f'某位患者的高压值是：{SBP}，低压值是：{DBP}，血糖是：{glucose}，甘油三酯是：{triglycerides}。请为该患者设计合理的运动建议。'
        response = get_LLM_response(prompt)

        response = markdown.markdown(response)

        # 在右侧显示诊断结果
        self.diagnosis_output.setHtml(response)

        # 启用运动处方按钮
        self.sport_prescription_button.setEnabled(True)
        self.response = response

    def open_sport_prescription_page(self):
        self.sport_prescription_window = SportPrescriptionPage(self.response)
        self.sport_prescription_window.show()