import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton, QTabWidget, QScrollArea,
                              QTextBrowser, QSplitter, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from fresh import LoadingScreen
from ai_for_halthy import get_AI_response

class HealthAssessmentPage(QWidget):
    def __init__(self, initial_data=None):
        super().__init__()
        self.setWindowTitle("健康评估")
        self.resize(800, 430)

        # 存储健康评估数据
        self.health_data = initial_data or ""

        # 解析AI返回内容的不同部分
        self.cardiovascular = ""  # 心血管健康
        self.metabolism = ""      # 糖脂代谢
        self.body_composition = "" # 体成分

        # 解析AI返回的内容
        self.parse_ai_content()

        # 创建UI
        self.init_ui()

        # 显示初始数据
        if initial_data:
            self.display_initial_data()
        else:
            self.show_default_message()

    def parse_ai_content(self):
        """解析AI返回的内容，分离出不同部分"""
        if not self.health_data:
            return

        # 寻找心血管健康部分
        if "心血管健康" in self.health_data:
            start = self.health_data.find("心血管健康")
            end = self.health_data.find("糖脂代谢") if "糖脂代谢" in self.health_data else len(self.health_data)
            self.cardiovascular = f"<h2>心血管健康评估</h2>{self.health_data[start+5:end - 8]}"

        # 寻找糖脂代谢部分
        if "糖脂代谢" in self.health_data:
            start = self.health_data.find("糖脂代谢")
            end = self.health_data.find("体成分") if "体成分" in self.health_data else len(self.health_data)
            self.metabolism = f"<h2>糖脂代谢评估</h2>{self.health_data[start+5:end - 8]}"

        # 寻找体成分部分
        if "体成分" in self.health_data:
            start = self.health_data.find("体成分")
            end = len(self.health_data)
            self.body_composition = f"<h2>体成分评估</h2>{self.health_data[start+3:end]}"

    def init_ui(self):
        """初始化界面"""
        # 主布局
        main_layout = QVBoxLayout(self)

        # 页面标题
        title_label = QLabel("健康评估报告")
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
            ("心血管健康", self.show_cardiovascular),
            ("糖脂代谢", self.show_metabolism),
            ("体成分", self.show_body_composition)
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

        self.print_btn = QPushButton("打印评估")
        self.print_btn.clicked.connect(self.print_report)

        self.save_btn = QPushButton("保存评估")
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

    def show_default_message(self):
        """显示默认消息"""
        self.content_browser.setHtml("""
            <h2>健康评估</h2>
            <p>请在主界面输入您的健康数据，然后点击"健康评估"按钮获取个性化健康评估报告。</p>
            <p>评估将包括：</p>
            <ul>
                <li>心血管健康状况</li>
                <li>糖脂代谢状况</li>
                <li>体成分分析</li>
            </ul>
        """)

    def show_cardiovascular(self):
        """显示心血管健康评估"""
        # 高亮当前按钮
        self.highlight_button(0)

        # 如果有AI生成的内容，则显示AI内容
        if self.cardiovascular:
            self.content_browser.setHtml(self.cardiovascular)
        else:
            # 无AI内容时显示默认内容
            self.content_browser.setHtml("""
            <h2>心血管健康评估</h2>
            <p>暂无个性化推荐，请输入您的健康数据并点击"健康评估"按钮获取。</p>
            """)

    def show_metabolism(self):
        """显示糖脂代谢评估"""
        # 高亮当前按钮
        self.highlight_button(1)

        # 如果有AI生成的内容，则显示AI内容
        if self.metabolism:
            self.content_browser.setHtml(self.metabolism)
        else:
            # 无AI内容时显示默认内容
            self.content_browser.setHtml("""
            <h2>糖脂代谢评估</h2>
            <p>暂无个性化推荐，请输入您的健康数据并点击"健康评估"按钮获取。</p>
            """)

    def show_body_composition(self):
        """显示体成分评估"""
        # 高亮当前按钮
        self.highlight_button(2)

        # 如果有AI生成的内容，则显示AI内容
        if self.body_composition:
            self.content_browser.setHtml(self.body_composition)
        else:
            # 无AI内容时显示默认内容
            self.content_browser.setHtml("""
            <h2>体成分评估</h2>
            <p>暂无个性化推荐，请输入您的健康数据并点击"健康评估"按钮获取。</p>
            """)

    def highlight_button(self, index):
        """高亮选中的导航按钮"""
        for i, button in enumerate(self.nav_buttons):
            if i == index:
                button.setStyleSheet("background-color: #0277BD; color: white;")
            else:
                button.setStyleSheet("")

    def print_report(self):
        """打印健康评估"""
        from PySide6.QtPrintSupport import QPrinter, QPrintDialog

        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)

        if dialog.exec() == QPrintDialog.Accepted:
            self.content_browser.print_(printer)

    def save_report(self):
        """保存健康评估为PDF"""
        from PySide6.QtWidgets import QFileDialog
        from PySide6.QtPrintSupport import QPrinter

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存健康评估",
            "健康评估报告.pdf",
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