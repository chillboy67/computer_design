'''
健康评估页面，显示用户的健康评估结果，包括心血管健康、糖脂代谢、体成分评估

-- wy 2025-02-26
'''



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
        self.resize(900, 600)

        # 存储健康数据
        self.health_data = initial_data or ""

        # 创建UI
        self.init_ui()

        # 显示初始数据
        if initial_data:
            self.display_initial_data()
        else:
            # 默认显示心血管健康评估
            self.show_cardiovascular()

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

        # 创建导航按钮（移除“综合评估”按钮）
        self.nav_buttons = []
        nav_items = [
            ("心血管健康评估", self.show_cardiovascular),
            ("糖脂代谢评估", self.show_metabolism),
            ("体成分评估", self.show_body_composition)
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

        self.print_btn = QPushButton("打印报告")
        self.print_btn.clicked.connect(self.print_report)

        self.save_btn = QPushButton("保存报告")
        self.save_btn.clicked.connect(self.save_report)

        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)

        bottom_layout.addWidget(self.print_btn)
        bottom_layout.addWidget(self.save_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.close_btn)

        main_layout.addLayout(bottom_layout)

    def display_initial_data(self):
        """显示从主窗口传递的初始健康数据"""
        self.content_browser.setHtml(self.health_data)
        # 默认显示心血管健康评估
        self.show_cardiovascular()

    def show_cardiovascular(self):
        """显示心血管健康评估"""
        # 高亮当前按钮
        self.highlight_button(0)

        # 尝试从完整数据中提取心血管部分
        if self.health_data and "心血管健康" in self.health_data:
            try:
                start_index = self.health_data.find("<h2>心血管健康")
                if start_index == -1:
                    start_index = self.health_data.find("<h3>心血管健康")

                end_index = self.health_data.find("<h2>", start_index + 1)
                if end_index == -1:
                    end_index = self.health_data.find("<h3>", start_index + 1)

                if start_index != -1 and end_index != -1:
                    section = self.health_data[start_index:end_index]
                    self.content_browser.setHtml(f"""
                    {section}
                    <p><a href="#" onclick="return false;">返回完整评估</a></p>
                    """)
                    return
            except Exception:
                pass

        # 如果无法提取或数据不存在，显示默认内容
        self.content_browser.setHtml("""
        <h2>心血管健康评估</h2>
        <p>基于您提供的血压和其他指标，以下是您的心血管健康状况评估：</p>
        <ul>
            <li><strong>血压状态：</strong>根据您提供的数据，您的血压处于正常/偏高/高血压范围。</li>
            <li><strong>心脏功能：</strong>基于心率和其他指标的评估结果。</li>
            <li><strong>血管弹性：</strong>血管健康状况评估。</li>
        </ul>
        <p>以上评估基于您提供的数据，如有不适请咨询医生获取专业建议。</p>
        """)

    def show_metabolism(self):
        """显示糖脂代谢评估"""
        # 高亮当前按钮
        self.highlight_button(1)

        # 尝试从完整数据中提取代谢部分
        if self.health_data and "糖脂代谢" in self.health_data:
            try:
                start_index = self.health_data.find("<h2>糖脂代谢")
                if start_index == -1:
                    start_index = self.health_data.find("<h3>糖脂代谢")

                end_index = self.health_data.find("<h2>", start_index + 1)
                if end_index == -1:
                    end_index = self.health_data.find("<h3>", start_index + 1)

                if start_index != -1 and end_index != -1:
                    section = self.health_data[start_index:end_index]
                    self.content_browser.setHtml(f"""
                    {section}
                    <p><a href="#" onclick="return false;">返回完整评估</a></p>
                    """)
                    return
            except Exception:
                pass

        self.content_browser.setHtml("""
        <h2>糖脂代谢评估</h2>
        <p>基于您提供的血糖和甘油三酯数据，以下是您的代谢健康状况：</p>
        <ul>
            <li><strong>血糖水平：</strong>您的空腹血糖水平分析。</li>
            <li><strong>血脂状况：</strong>甘油三酯水平及其对健康的影响。</li>
            <li><strong>代谢综合评分：</strong>基于多项指标的综合代谢健康评分。</li>
        </ul>
        <p>良好的糖脂代谢对预防心血管疾病和糖尿病至关重要。</p>
        """)

    def show_body_composition(self):
        """显示体成分评估"""
        # 高亮当前按钮
        self.highlight_button(2)

        # 尝试从完整数据中提取体成分部分
        if self.health_data and "体成分" in self.health_data:
            try:
                start_index = self.health_data.find("<h2>体成分")
                if start_index == -1:
                    start_index = self.health_data.find("<h3>体成分")

                end_index = self.health_data.find("<h2>", start_index + 1)
                if end_index == -1:
                    end_index = self.health_data.find("<h3>", start_index + 1)
                    if end_index == -1:
                        end_index = len(self.health_data)

                if start_index != -1:
                    section = self.health_data[start_index:end_index]
                    self.content_browser.setHtml(f"""
                    {section}
                    <p><a href="#" onclick="return false;">返回完整评估</a></p>
                    """)
                    return
            except Exception:
                pass

        self.content_browser.setHtml("""
        <h2>体成分评估</h2>
        <p>体成分分析对了解身体的肌肉、脂肪分布非常重要：</p>
        <ul>
            <li><strong>体重指数(BMI)：</strong>基于身高体重计算的BMI值及其分类。</li>
            <li><strong>体脂率：</strong>体内脂肪占总体重的百分比及评估。</li>
            <li><strong>肌肉含量：</strong>肌肉质量评估及其对新陈代谢的影响。</li>
            <li><strong>内脏脂肪：</strong>内脏周围脂肪堆积水平及其健康风险评估。</li>
        </ul>
        <p>合理的体成分对整体健康和疾病预防具有重要意义。</p>
        """)

    def highlight_button(self, index):
        """高亮选中的导航按钮"""
        for i, button in enumerate(self.nav_buttons):
            if i == index:
                button.setStyleSheet("background-color: #0277BD; color: white;")
            else:
                button.setStyleSheet("")

    def print_report(self):
        """打印健康报告"""
        from PySide6.QtPrintSupport import QPrinter, QPrintDialog

        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)

        if dialog.exec() == QPrintDialog.Accepted:
            self.content_browser.print_(printer)

    def save_report(self):
        """保存健康报告为PDF"""
        from PySide6.QtWidgets import QFileDialog
        from PySide6.QtPrintSupport import QPrinter

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存健康报告",
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
