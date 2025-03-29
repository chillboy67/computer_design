'''
运动处方页面，显示用户的运动处方结果，包括运动项目、运动频率、运动强度

-- wy 2025-02-26
'''

import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton, QTabWidget, QScrollArea,
                              QTextBrowser, QSplitter)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from fresh import LoadingScreen
from llm_utils import get_LLM_response

class SportPrescriptionPage(QWidget):
    def __init__(self, initial_data=None):
        super().__init__()
        self.setWindowTitle("运动处方")
        self.resize(900, 600)

        # 存储运动数据
        self.health_data = initial_data or ""

        # 创建UI
        self.init_ui()

        # 显示初始数据
        if initial_data:
            self.display_initial_data()
        else:
            # 默认显示运动项目建议
            self.show_cardiovascular()

    def init_ui(self):
        """初始化界面"""
        # 主布局
        main_layout = QVBoxLayout(self)

        # 页面标题
        title_label = QLabel("运动处方报告")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 创建分隔器
        splitter = QSplitter(Qt.Horizontal)

        # 左侧导航面板
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)

        self.nav_buttons = []
        nav_items = [
            ("运动项目", self.show_cardiovascular),
            ("运动频率", self.show_metabolism),
            ("运动强度", self.show_body_composition)
        ]

        for text, callback in nav_items:
            button = QPushButton(text)
            button.setMinimumHeight(50)
            button.clicked.connect(callback)
            nav_layout.addWidget(button)
            self.nav_buttons.append(button)



        nav_layout.addStretch()
        splitter.addWidget(nav_widget)

        # 右侧内容面板
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # 内容显示区域
        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(True)
        self.content_browser.setFont(QFont("Arial", 11))
        content_layout.addWidget(self.content_browser)

        splitter.addWidget(content_widget)

        # 设置分隔器的初始比例
        splitter.setSizes([200, 700])

        # 将分隔器添加到主布局
        main_layout.addWidget(splitter)

        # 底部操作按钮区域
        bottom_layout = QHBoxLayout()

        self.print_btn = QPushButton("打印处方")
        self.print_btn.clicked.connect(self.print_report)

        self.save_btn = QPushButton("保存处方")
        self.save_btn.clicked.connect(self.save_report)

        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)

        bottom_layout.addWidget(self.print_btn)
        bottom_layout.addWidget(self.save_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.close_btn)

        main_layout.addLayout(bottom_layout)

    def display_initial_data(self):
        """显示从主窗口传递的初始运动数据"""
        self.content_browser.setHtml(self.health_data)
        # 默认显示运动项目建议
        self.show_cardiovascular()

    def show_cardiovascular(self):
        """显示运动项目推荐"""
        # 高亮当前按钮
        self.highlight_button(0)

        # 显示运动项目建议内容
        self.content_browser.setHtml("""
        <h2>运动项目</h2>
        <p>基于您的身体状况和运动喜好，以下是为您推荐的运动项目：</p>
        <ul>
            <li><strong>推荐运动：</strong>根据您的体能和偏好，建议进行适合的有氧或力量训练。</li>
            <li><strong>运动目标：</strong>帮助提升心肺功能及整体健康。</li>
            <li><strong>活动建议：</strong>结合多种运动方式，确保运动多样性。</li>
        </ul>
        <p>以上建议仅供参考，如有疑问请咨询专业教练。</p>
        """)

    def show_metabolism(self):
        """显示运动频率建议"""
        # 高亮当前按钮
        self.highlight_button(1)

        self.content_browser.setHtml("""
        <h2>运动频率</h2>
        <p>基于您的生活习惯和体能状况，以下是为您推荐的运动频率建议：</p>
        <ul>
            <li><strong>每周运动次数：</strong>建议每周至少进行3-5次运动。</li>
            <li><strong>运动时长：</strong>每次运动建议持续30-60分钟。</li>
            <li><strong>频率调整：</strong>根据您的体能进步逐步调整运动频率。</li>
        </ul>
        <p>合理的运动频率有助于提升健康和保持体能。</p>
        """)

    def show_body_composition(self):
        """显示运动强度建议"""
        # 高亮当前按钮
        self.highlight_button(2)

        self.content_browser.setHtml("""
        <h2>运动强度</h2>
        <p>运动强度的合理控制对达到运动效果至关重要：</p>
        <ul>
            <li><strong>低强度运动：</strong>适合初学者和恢复期人群，保持轻松运动。</li>
            <li><strong>中等强度运动：</strong>提升心肺功能和燃脂效果的理想选择。</li>
            <li><strong>高强度运动：</strong>适用于有一定基础的人群，挑战自我极限。</li>
        </ul>
        <p>根据个人体能选择合适的运动强度，确保运动安全和效果。</p>
        """)


    def handle_ai_response(self, response):
        """处理AI响应并显示结果"""
        # 将AI返回的评估结果转换为HTML格式
        html_content = f"""
        <h2>个性化运动处方</h2>
        <div class="ai-assessment">
            {response}
        </div>
        """

        # 更新显示内容
        self.content_browser.setHtml(html_content)
        self.health_data = html_content

        # 高亮运动项目按钮（默认）
        self.highlight_button(0)

    def highlight_button(self, index):
        """高亮选中的导航按钮"""
        for i, button in enumerate(self.nav_buttons):
            if i == index:
                button.setStyleSheet("background-color: #0277BD; color: white;")
            else:
                button.setStyleSheet("")

    def print_report(self):
        """打印运动处方"""
        from PySide6.QtPrintSupport import QPrinter, QPrintDialog

        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)

        if dialog.exec() == QPrintDialog.Accepted:
            self.content_browser.print_(printer)

    def save_report(self):
        """保存运动处方为PDF"""
        from PySide6.QtWidgets import QFileDialog
        from PySide6.QtPrintSupport import QPrinter

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存运动处方",
            "运动处方报告.pdf",
            "PDF文件 (*.pdf)"
        )

        if file_path:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)
            self.content_browser.print_(printer)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HealthAssessmentPage()
    window.show()
    sys.exit(app.exec())
