import logging

from PySide6.QtCore import (Property, QEasingCurve, QPropertyAnimation, Qt,
                            QThread, QTimer, Signal)
from PySide6.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QMessageBox, QPushButton, QVBoxLayout

import config
from llm_utils import LLMError

logger = logging.getLogger(__name__)

# 仍在运行的后台线程。用户取消等待后线程还会继续跑完，需要保留引用防止被提前回收
_active_workers = set()


def _track_worker(worker):
    for finished in [w for w in _active_workers if w.isFinished()]:
        _active_workers.discard(finished)
    _active_workers.add(worker)


class ImageBrightener(QLabel):
    """自定义widget，显示图片并从底部逐渐变亮"""

    def __init__(self, image_path, parent=None):
        super().__init__(parent)

        # 加载图片
        self.original_pixmap = QPixmap(image_path)
        if self.original_pixmap.isNull():
            # 如果无法加载图片，创建一个默认的灰色图片
            logger.warning("加载图片失败：%s", image_path)
            self.original_pixmap = QPixmap(300, 200)
            self.original_pixmap.fill(QColor(200, 200, 200))

        # 调整图片大小，保持合理尺寸
        if self.original_pixmap.width() > 500 or self.original_pixmap.height() > 400:
            self.original_pixmap = self.original_pixmap.scaled(500, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # 设置图片大小
        self.setFixedSize(self.original_pixmap.width(), self.original_pixmap.height())

        # 亮度属性，0表示完全暗，1表示完全亮
        self._brightness = 0.0

        # 初始设置
        self.updatePixmap()

    def getBrightness(self):
        return self._brightness

    def setBrightness(self, value):
        self._brightness = value
        self.updatePixmap()

    # 定义亮度属性
    brightness = Property(float, getBrightness, setBrightness)

    def updatePixmap(self):
        """根据当前亮度更新图片"""
        result = QPixmap(self.original_pixmap.size())
        result.fill(Qt.transparent)

        painter = QPainter(result)

        # 创建渐变遮罩 - 底部亮，顶部暗
        gradient = QLinearGradient(0, 0, 0, self.height())

        # 计算亮度分界点位置
        boundary = 1.0 - self._brightness

        gradient.setColorAt(0, QColor(255, 255, 255, 0))  # 顶部完全透明
        gradient.setColorAt(boundary, QColor(255, 255, 255, 0))  # 分界点完全透明
        gradient.setColorAt(min(1.0, boundary + 0.05), QColor(255, 255, 255, 255))  # 分界点下方完全不透明
        gradient.setColorAt(1, QColor(255, 255, 255, 255))  # 底部完全不透明

        # 绘制原始图片，再使用渐变作为遮罩
        painter.drawPixmap(0, 0, self.original_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.fillRect(result.rect(), QBrush(gradient))
        painter.end()

        self.setPixmap(result)


class LoadingWorker(QThread):
    """在后台线程中执行AI请求，避免界面卡死"""
    succeeded = Signal(str)
    failed = Signal(str)

    def __init__(self, ai_function, prompt):
        super().__init__()
        self.ai_function = ai_function
        self.prompt = prompt

    def run(self):
        try:
            self.succeeded.emit(self.ai_function(self.prompt))
        except LLMError as e:
            self.failed.emit(str(e))
        except Exception as e:
            logger.exception("生成内容时出错")
            self.failed.emit(f"生成内容时出错：{e}")


class LoadingScreen(QDialog):
    """加载屏幕，显示等待AI响应的过程"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("请稍候")
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setModal(True)

        layout = QVBoxLayout(self)

        self.image_widget = ImageBrightener(str(config.LOADING_IMAGE))
        layout.addWidget(self.image_widget, 0, Qt.AlignCenter)

        self.status_label = QLabel("正在生成AI内容，请稍候...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(self.status_label)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button, 0, Qt.AlignCenter)

        self.adjustSize()

        # 亮度动画 - 等待期间缓慢变亮到70%
        self.brightness_animation = QPropertyAnimation(self.image_widget, b"brightness")
        self.brightness_animation.setDuration(20000)
        self.brightness_animation.setStartValue(0.0)
        self.brightness_animation.setEndValue(0.7)
        self.brightness_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # 最终亮度动画 - 收到结果后快速完全变亮
        self.final_animation = QPropertyAnimation(self.image_widget, b"brightness")
        self.final_animation.setDuration(1200)
        self.final_animation.setEndValue(1.0)
        self.final_animation.setEasingCurve(QEasingCurve.OutQuad)

        self._response = None
        self._error = None
        self._cancelled = False
        self.close_timer = QTimer(self)
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self.accept)

    def start_loading(self, ai_function, prompt, callback):
        """
        在后台调用 AI，期间显示加载动画；成功后调用 callback(response)，失败时弹出提示

        Args:
            ai_function: 调用AI的函数，如 get_health_assessment
            prompt: 要发送给AI的提示文本
            callback: 成功后的回调函数
        """
        worker = LoadingWorker(ai_function, prompt)
        worker.succeeded.connect(self._on_success)
        worker.failed.connect(self._on_failure)
        _track_worker(worker)

        self.brightness_animation.start()
        worker.start()

        if self.exec() and self._response is not None:
            callback(self._response)
        elif self._error:
            QMessageBox.warning(self.parentWidget(), "生成失败", self._error)

    def reject(self):
        """点击“取消”或按 Esc 时停止等待，后台请求返回的结果将被丢弃"""
        self._cancelled = True
        self.close_timer.stop()
        self.brightness_animation.stop()
        super().reject()

    def _on_success(self, response):
        if self._cancelled:
            return
        self._response = response
        self.cancel_button.setEnabled(False)
        self.status_label.setText("生成完成，正在处理...")

        # 停止当前动画并启动最终亮度动画，动画结束后关闭对话框
        self.brightness_animation.stop()
        self.final_animation.setStartValue(self.image_widget.brightness)
        self.final_animation.start()
        self.close_timer.start(1500)

    def _on_failure(self, message):
        if self._cancelled:
            return
        self._error = message
        self.reject()
