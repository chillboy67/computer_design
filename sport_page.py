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
        self.resize(800, 430)

        # 存储运动数据
        self.health_data = initial_data or ""

        # 解析AI返回内容的不同部分
        self.exercise_types = ""  # 运动项目
        self.exercise_frequency = ""  # 运动频率
        self.exercise_intensity = ""  # 运动强度
        self.parse_ai_content()

        # 创建UI
        self.init_ui()

        # 显示初始数据
        if initial_data:
            self.display_initial_data()
        else:
            # 默认显示运动项目建议
            self.show_cardiovascular()

    def parse_ai_content(self):
        """解析AI返回的内容，分离出不同部分"""
        if not self.health_data:
            return

        # 寻找运动项目部分
        if "运动项目" in self.health_data:
            start = self.health_data.find("运动项目")
            end = self.health_data.find("运动频率") if "运动频率" in self.health_data else len(self.health_data)
            self.exercise_types = f"<h2>运动项目</h2>{self.health_data[start + 4:end - 8]}"

        # 寻找运动频率部分
        if "运动频率" in self.health_data:
            start = self.health_data.find("运动频率")
            end = self.health_data.find("运动强度") if "运动强度" in self.health_data else len(self.health_data)
            self.exercise_frequency = f"<h2>运动频率</h2>{self.health_data[start + 4:end - 8]}"

        # 寻找运动强度部分
        if "运动强度" in self.health_data:
            start = self.health_data.find("运动强度")
            end = len(self.health_data)
            self.exercise_intensity = f"<h2>运动强度</h2>{self.health_data[start + 4:end]}"


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
        # 解析数据后直接显示运动项目
        self.show_cardiovascular()  # 你需要创建这个方法
        # 高亮第一个按钮
        self.highlight_button(0)

    def show_cardiovascular(self):
        """显示运动项目推荐"""
        # 高亮当前按钮
        self.highlight_button(0)

        # 如果有AI生成的内容，则显示AI内容
        if self.exercise_types:
            self.content_browser.setHtml(self.exercise_types)
        else:
            # 无AI内容时显示默认内容
            self.content_browser.setHtml("""
                <h2>运动项目</h2>
                <p>基于您的身体状况和运动喜好，以下是为您推荐的运动项目：</p>
                <p>暂无个性化推荐，请输入您的健康数据并点击"运动处方"按钮获取。</p>
                """)

    def show_metabolism(self):
        """显示运动频率建议"""
        # 高亮当前按钮
        self.highlight_button(1)

        # 如果有AI生成的内容，则显示AI内容
        if self.exercise_frequency:
            self.content_browser.setHtml(self.exercise_frequency)
        else:
            # 无AI内容时显示默认内容
            self.content_browser.setHtml("""
            <h2>运动频率</h2>
            <p>暂无个性化推荐，请输入您的健康数据并点击"运动处方"按钮获取。</p>
            """)

    def show_body_composition(self):
        """显示运动强度建议"""
        # 高亮当前按钮
        self.highlight_button(2)

        # 如果有AI生成的内容，则显示AI内容
        if self.exercise_intensity:
            self.content_browser.setHtml(self.exercise_intensity)
        else:
            # 无AI内容时显示默认内容
            self.content_browser.setHtml("""
            <h2>运动强度</h2>
            <p>暂无个性化推荐，请输入您的健康数据并点击"运动处方"按钮获取。</p>
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
    window = SportPrescriptionPage()
    window.show()
    sys.exit(app.exec())