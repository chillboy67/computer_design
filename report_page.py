"""健康评估、运动处方两个报告页面的公共部分"""
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QTextDocument
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QMessageBox,
                               QPushButton, QSplitter, QTextBrowser, QVBoxLayout,
                               QWidget)

from prompts import split_sections

DISCLAIMER = "提示：本报告由 AI 生成，仅供健康管理参考，不能替代医生的诊断和治疗。"
FULL_REPORT = "完整报告"


class ReportPage(QWidget):
    """左侧导航 + 右侧内容的报告页面，子类只需声明标题和分节

    既可以直接展示已有报告，也可以通过 attach_stream() 实时展示正在生成的报告。
    """

    window_title = ""
    report_title = ""
    sections = ()  # 与 prompts 中要求 AI 输出的二级标题保持一致

    generation_finished = Signal(str)  # 流式生成成功结束，携带完整报告

    def __init__(self, report_text="", generated_at=None, parent=None):
        super().__init__(parent)
        self.generated_at = generated_at or datetime.now()
        title = self.window_title
        if generated_at:
            title += f"（{generated_at:%Y-%m-%d %H:%M}）"
        self.setWindowTitle(title)
        self.resize(860, 560)

        self.report_text = report_text or ""
        self.section_texts = {}
        self.nav_items = list(self.sections) + [FULL_REPORT]
        self.worker = None  # 正在生成时的 StreamWorker

        # 流式输出时限制重新渲染的频率
        self._render_timer = QTimer(self)
        self._render_timer.setSingleShot(True)
        self._render_timer.setInterval(150)
        self._render_timer.timeout.connect(self._render_stream)

        self.init_ui()
        self._show_finished_report()

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
        self.print_btn = QPushButton("打印报告")
        self.print_btn.clicked.connect(self.print_report)
        self.save_btn = QPushButton("保存为 PDF")
        self.save_btn.clicked.connect(self.save_report)
        self.status_label = QLabel()
        self.stop_btn = QPushButton("停止生成")
        self.stop_btn.clicked.connect(self.stop_generation)
        self.stop_btn.hide()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        bottom_layout.addWidget(self.print_btn)
        bottom_layout.addWidget(self.save_btn)
        bottom_layout.addWidget(self.status_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.stop_btn)
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

    def _show_finished_report(self):
        """拆分报告并显示第一部分；没能拆分出任何部分时直接展示完整报告"""
        self.section_texts = split_sections(self.report_text, self.sections)
        self.show_section(0 if self.section_texts else len(self.nav_items) - 1)

    # ---------- 流式生成 ----------

    def attach_stream(self, worker):
        """实时显示 worker 正在生成的内容，生成结束后再按标题拆分"""
        self.worker = worker
        self._set_generating(True)
        worker.progress.connect(self._on_stream_progress)
        worker.succeeded.connect(self._on_stream_succeeded)
        worker.failed.connect(self._on_stream_failed)

        # 连接信号之前 worker 可能已经输出了内容，甚至已经结束
        self.report_text = worker.text
        self._render_stream()
        if worker.done:
            if worker.error:
                self._on_stream_failed(worker.error)
            else:
                self._on_stream_succeeded(worker.text)

    def _set_generating(self, generating):
        for button in self.nav_buttons + [self.print_btn, self.save_btn]:
            button.setEnabled(not generating)
        self.stop_btn.setVisible(generating)
        if generating:
            self.highlight_button(len(self.nav_items) - 1)
            self._set_status("正在生成，请稍候...")

    def _set_status(self, text, error=False):
        self.status_label.setText(text)
        self.status_label.setStyleSheet("color: #D32F2F;" if error else "color: #0277BD;")

    def _on_stream_progress(self, text):
        if self.worker is None:
            return
        self.report_text = text
        if not self._render_timer.isActive():
            self._render_timer.start()

    def _render_stream(self):
        """渲染当前已生成的内容；用户正在看末尾时自动滚动到底部"""
        scrollbar = self.content_browser.verticalScrollBar()
        at_bottom = scrollbar.value() >= scrollbar.maximum() - 4
        self.content_browser.setMarkdown(self.report_text or "正在生成...")
        if at_bottom:
            scrollbar.setValue(scrollbar.maximum())

    def _finish_stream(self, text):
        """流式生成结束（成功、失败或停止）后的公共处理，返回 False 表示已经处理过"""
        if self.worker is None:
            return False
        self.worker = None
        self._render_timer.stop()
        self.report_text = text
        self._set_generating(False)
        self._show_finished_report()
        return True

    def _on_stream_succeeded(self, text):
        if self._finish_stream(text):
            self._set_status("生成完成")
            self.generation_finished.emit(text)

    def _on_stream_failed(self, message):
        if self._finish_stream(self.report_text):
            self._set_status("生成中断，内容可能不完整", error=True)
            QMessageBox.warning(self, "生成失败", message)

    def stop_generation(self):
        worker = self.worker
        if worker and self._finish_stream(self.report_text):
            worker.stop()
            self._set_status("已停止生成，内容不完整", error=True)

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
            self.worker = None
        super().closeEvent(event)

    # ---------- 打印和导出 ----------

    def build_document(self):
        """生成用于打印/导出的完整报告（包含全部内容，而不只是当前页）"""
        document = QTextDocument(self)
        document.setMarkdown(
            f"# {self.report_title}\n\n"
            f"生成时间：{self.generated_at:%Y-%m-%d %H:%M}\n\n"
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
