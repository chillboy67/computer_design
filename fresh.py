# fresh.py
'''
加载页面代码，显示等待AI响应的过程

-- wy 2025-02-26
'''

import sys
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QTimer, Signal, QThread


class LoadingWorker(QThread):
    """在后台线程中执行AI请求的工作类"""
    finished = Signal(str)  # 结束信号，携带响应内容

    def __init__(self, ai_function, prompt):
        super().__init__()
        self.ai_function = ai_function
        self.prompt = prompt

    def run(self):
        """执行AI调用并发送结果"""
        response = self.ai_function(self.prompt)
        self.finished.emit(response)


class LoadingScreen(QDialog):
    """加载屏幕，显示等待AI响应的过程"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("请稍候")
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setFixedSize(300, 150)
        self.setModal(True)

        # 创建UI元素
        layout = QVBoxLayout(self)

        self.status_label = QLabel("正在生成AI内容，请稍候...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # 设置为忙碌状态
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        # 请求结果
        self.result = None
        self.worker = None

    def start_loading(self, ai_function, prompt, callback):
        """
        开始加载过程

        Args:
            ai_function: 调用AI的函数 (get_LLM_response 或 get_AI_response)
            prompt: 要发送给AI的提示文本
            callback: 完成后的回调函数
        """
        # 创建工作线程
        self.worker = LoadingWorker(ai_function, prompt)
        self.worker.finished.connect(self._on_ai_response)
        self.worker.finished.connect(lambda response: callback(response))

        # 显示对话框并启动工作线程
        self.worker.start()
        self.exec()

    def _on_ai_response(self, response):
        """AI响应完成后关闭对话框"""
        self.result = response
        self.accept()