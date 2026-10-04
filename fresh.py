import logging
import time

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


class StreamWorker(QThread):
    """在后台线程中流式调用AI，避免界面卡死

    progress 携带截至目前的完整文本；结束时发出 succeeded 或 failed（被 stop 时两者都不发）。
    text / error / done 也作为属性保存，晚连接的接收方可以据此补上错过的信号。
    """
    progress = Signal(str)
    succeeded = Signal(str)
    failed = Signal(str)

    PROGRESS_INTERVAL = 0.1  # 秒，限制刷新频率

    def __init__(self, stream_function, prompt):
        super().__init__()
        self.stream_function = stream_function
        self.prompt = prompt
        self.text = ""
        self.error = None
        self.done = False
        self._stopped = False

    def stop(self):
        """请求停止生成，后台线程会在收到下一段内容时退出"""
        self._stopped = True

    def run(self):
        last_emit = 0.0
        try:
            stream = self.stream_function(self.prompt)
            for piece in stream:
                if self._stopped:
                    close = getattr(stream, "close", None)
                    if close:
                        close()
                    return
                self.text += piece
                now = time.monotonic()
                if now - last_emit >= self.PROGRESS_INTERVAL:
                    last_emit = now
                    self.progress.emit(self.text)
            if not self.text.strip():
                raise LLMError("AI 服务返回了空内容，请稍后重试")
        except LLMError as e:
            self.error = str(e)
        except Exception as e:
            logger.exception("生成内容时出错")
            self.error = f"生成内容时出错：{e}"
        if self._stopped:
            return
        self.done = True
        if self.error:
            self.failed.emit(self.error)
        else:
            self.succeeded.emit(self.text)


class LoadingScreen(QDialog):
    """加载屏幕：等待AI开始输出期间显示动画"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("请稍候")
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setModal(True)

        layout = QVBoxLayout(self)

        self.image_widget = ImageBrightener(str(config.LOADING_IMAGE))
        layout.addWidget(self.image_widget, 0, Qt.AlignCenter)

        self.status_label = QLabel("正在连接AI服务，请稍候...", self)
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

        # 最终亮度动画 - 开始输出后快速完全变亮
        self.final_animation = QPropertyAnimation(self.image_widget, b"brightness")
        self.final_animation.setDuration(600)
        self.final_animation.setEndValue(1.0)
        self.final_animation.setEasingCurve(QEasingCurve.OutQuad)

        self._started = False
        self._error = None
        self._cancelled = False
        self.close_timer = QTimer(self)
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self.accept)

    def wait_for_output(self, worker):
        """
        启动 worker 并显示加载动画，直到 AI 开始输出

        Returns:
            True 表示已开始输出（worker 继续在后台生成）；False 表示失败或被用户取消
        """
        worker.progress.connect(self._on_output)
        worker.succeeded.connect(self._on_output)
        worker.failed.connect(self._on_failure)
        _track_worker(worker)

        self.brightness_animation.start()
        worker.start()
        started = bool(self.exec())

        worker.progress.disconnect(self._on_output)
        worker.succeeded.disconnect(self._on_output)
        worker.failed.disconnect(self._on_failure)
        if not started:
            worker.stop()
            if self._error:
                QMessageBox.warning(self.parentWidget(), "生成失败", self._error)
        return started

    def reject(self):
        """点击“取消”或按 Esc 时停止等待"""
        self._cancelled = True
        self.close_timer.stop()
        self.brightness_animation.stop()
        super().reject()

    def _on_output(self, _text):
        if self._cancelled or self._started:
            return
        self._started = True
        self.cancel_button.setEnabled(False)
        self.status_label.setText("AI 已开始输出...")

        # 停止当前动画并启动最终亮度动画，动画结束后关闭对话框
        self.brightness_animation.stop()
        self.final_animation.setStartValue(self.image_widget.brightness)
        self.final_animation.start()
        self.close_timer.start(700)

    def _on_failure(self, message):
        if self._cancelled or self._started:  # 已开始输出时由报告页展示已生成的部分和错误
            return
        self._error = message
        self.reject()
