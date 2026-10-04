"""健康评估、运动处方两个报告页面的公共部分"""
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextDocument
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QMessageBox,
                               QPushButton, QSplitter, QTextBrowser, QVBoxLayout,
                               QWidget)

from prompts import split_sections

DISCLAIMER = "提示：本报告由 AI 生成，仅供健康管理参考，不能替代医生的诊断和治疗。"
FULL_REPORT = "完整报告"


class ReportPage(QWidget):
    """左侧导航 + 右侧内容的报告页面，子类只需声明标题和分节"""

    window_title = ""
    report_title = ""
    sections = ()  # 与 prompts 中要求 AI 输出的二级标题保持一致

    def __init__(self, report_text="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.window_title)
        self.resize(860, 520)

        self.report_text = report_text or ""
        self.section_texts = split_sections(self.report_text, self.sections)
        self.nav_items = list(self.sections) + [FULL_REPORT]

        self.init_ui()
        # 没能拆分出任何部分时直接展示完整报告
        self.show_section(0 if self.section_texts else len(self.nav_items) - 1)

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        title_label = QLabel(self.report_title)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        splitter = QSplitter(Qt.Horizontal)

        # 左侧导航
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        self.nav_buttons = []
        for index, text in enumerate(self.nav_items):
            button = QPushButton(text)
            button.setMinimumHeight(50)
            button.clicked.connect(lambda _=False, i=index: self.show_section(i))
            nav_layout.addWidget(button)
            self.nav_buttons.append(button)
        nav_layout.addStretch()
        splitter.addWidget(nav_widget)

        # 右侧内容
        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(True)
        self.content_browser.setFont(QFont("Arial", 11))
        splitter.addWidget(self.content_browser)
        splitter.setSizes([180, 680])
        main_layout.addWidget(splitter, 1)  # 内容区域占据剩余空间

        disclaimer = QLabel(DISCLAIMER)
        disclaimer.setStyleSheet("color: #888888;")
        disclaimer.setWordWrap(True)
        main_layout.addWidget(disclaimer)

        # 底部操作按钮
        bottom_layout = QHBoxLayout()
        print_btn = QPushButton("打印报告")
        print_btn.clicked.connect(self.print_report)
        save_btn = QPushButton("保存为 PDF")
        save_btn.clicked.connect(self.save_report)
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        bottom_layout.addWidget(print_btn)
        bottom_layout.addWidget(save_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(close_btn)
        main_layout.addLayout(bottom_layout)

    def show_section(self, index):
        title = self.nav_items[index]
        if title == FULL_REPORT:
            markdown = self.report_text or "暂无内容"
        else:
            body = self.section_texts.get(title) or f"AI 未单独给出“{title}”部分，请查看“{FULL_REPORT}”。"
            markdown = f"## {title}\n\n{body}"
        self.content_browser.setMarkdown(markdown)
        self.highlight_button(index)

    def highlight_button(self, index):
        for i, button in enumerate(self.nav_buttons):
            button.setStyleSheet("background-color: #0277BD; color: white;" if i == index else "")

    def build_document(self):
        """生成用于打印/导出的完整报告（包含全部内容，而不只是当前页）"""
        document = QTextDocument(self)
        document.setMarkdown(
            f"# {self.report_title}\n\n"
            f"生成时间：{datetime.now():%Y-%m-%d %H:%M}\n\n"
            f"{self.report_text}\n\n---\n\n{DISCLAIMER}"
        )
        return document

    def print_report(self):
        printer = QPrinter(QPrinter.HighResolution)
        if QPrintDialog(printer, self).exec():
            self.build_document().print_(printer)

    def save_report(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存报告", f"{self.report_title}.pdf", "PDF 文件 (*.pdf)"
        )
        if not file_path:
            return
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_path)
        self.build_document().print_(printer)
        QMessageBox.information(self, "保存成功", f"报告已保存到：\n{file_path}")
