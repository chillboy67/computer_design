# sport_page.py
import sys
import re
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QMessageBox, QGridLayout
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


class SportPrescriptionPage(QWidget):
    def __init__(self, response):
        super().__init__()
        self.response = response
        self.initUI()

    def initUI(self):
        self.setWindowTitle('运动处方页面')
        self.setGeometry(100, 100, 800, 400)
        self.setStyleSheet("background-color: #f0f0f0;")

        layout = QGridLayout()
        layout.setSpacing(10)

        # 标题
        title_label = QLabel('运动处方')
        title_label.setFont(QFont('楷体', 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label, 0, 0, 1, 2)

        # 解析运动建议
        exercise, frequency, intensity = self.parse_response(self.response)

        # 运动项目模块
        self.exercise_label = QLabel('运动项目:')
        self.exercise_label.setFont(QFont('楷体', 14, QFont.Bold))
        self.exercise_display = QTextEdit()
        self.exercise_display.setPlainText(exercise)
        self.exercise_display.setReadOnly(True)
        layout.addWidget(self.exercise_label, 1, 0)
        layout.addWidget(self.exercise_display, 1, 1)

        # 运动频率模块
        self.frequency_label = QLabel('运动频率:')
        self.frequency_label.setFont(QFont('楷体', 14, QFont.Bold))
        self.frequency_display = QTextEdit()
        self.frequency_display.setPlainText(frequency)
        self.frequency_display.setReadOnly(True)
        layout.addWidget(self.frequency_label, 2, 0)
        layout.addWidget(self.frequency_display, 2, 1)

        # 运动强度模块
        self.intensity_label = QLabel('运动强度:')
        self.intensity_label.setFont(QFont('楷体', 14, QFont.Bold))
        self.intensity_display = QTextEdit()
        self.intensity_display.setPlainText(f"{intensity}%")
        self.intensity_display.setReadOnly(True)
        layout.addWidget(self.intensity_label, 3, 0)
        layout.addWidget(self.intensity_display, 3, 1)

        self.setLayout(layout)

    def parse_response(self, response):
        # 假设 AI 返回的格式是固定的
        exercise_match = re.search(r'运动项目:\s*(.*)', response)
        frequency_match = re.search(r'运动频率:\s*每周\s*(\d+)\s*次', response)
        intensity_match = re.search(r'运动强度:\s*心率的\s*(\d+)%', response)

        exercise = exercise_match.group(1).strip() if exercise_match else '无数据'
        frequency = frequency_match.group(1).strip() if frequency_match else '无数据'
        intensity = intensity_match.group(1).strip() if intensity_match else '无数据'

        return exercise, frequency, intensity

