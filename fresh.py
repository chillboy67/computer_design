# import sys
# import os
# from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel)
# from PySide6.QtCore import Qt, Signal, QThread, QPropertyAnimation, QEasingCurve, Property, QTimer
# from PySide6.QtGui import QPixmap, QPainter, QColor, QLinearGradient, QBrush, QFont
#
#
# class ImageBrightener(QLabel):
#     """自定义widget，显示图片并从底部逐渐变亮"""
#
#     def __init__(self, image_path, parent=None):
#         super().__init__(parent)
#
#         # 加载图片
#         self.original_pixmap = QPixmap(image_path)
#         if self.original_pixmap.isNull():
#             # 如果无法加载图片，创建一个默认的灰色图片
#             self.original_pixmap = QPixmap(300, 200)
#             self.original_pixmap.fill(QColor(200, 200, 200))
#
#         # 调整图片大小，保持合理尺寸
#         if self.original_pixmap.width() > 500 or self.original_pixmap.height() > 400:
#             self.original_pixmap = self.original_pixmap.scaled(500, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
#
#         # 设置图片大小
#         self.setFixedSize(self.original_pixmap.width(), self.original_pixmap.height())
#
#         # 亮度属性，0表示完全暗，1表示完全亮
#         self._brightness = 0.0
#
#         # 初始设置
#         self.updatePixmap()
#
#     def getBrightness(self):
#         return self._brightness
#
#     def setBrightness(self, value):
#         self._brightness = value
#         self.updatePixmap()
#
#     # 定义亮度属性
#     brightness = Property(float, getBrightness, setBrightness)
#
#     def updatePixmap(self):
#         """根据当前亮度更新图片"""
#         # 创建绘图
#         result = QPixmap(self.original_pixmap.size())
#         result.fill(Qt.transparent)
#
#         painter = QPainter(result)
#
#         # 创建渐变遮罩 - 底部亮，顶部暗
#         gradient = QLinearGradient(0, 0, 0, self.height())
#
#         # 计算亮度分界点位置
#         boundary = (1.0 - self._brightness) * self.height()
#
#         gradient.setColorAt(0, QColor(255, 255, 255, 0))  # 顶部完全透明
#         gradient.setColorAt(boundary / self.height(), QColor(255, 255, 255, 0))  # 分界点完全透明
#         gradient.setColorAt(min(1.0, boundary / self.height() + 0.05), QColor(255, 255, 255, 255))  # 分界点下方完全不透明
#         gradient.setColorAt(1, QColor(255, 255, 255, 255))  # 底部完全不透明
#
#         # 绘制原始图片
#         painter.drawPixmap(0, 0, self.original_pixmap)
#
#         # 使用渐变作为遮罩
#         painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
#         painter.fillRect(result.rect(), QBrush(gradient))
#
#         painter.end()
#
#         # 设置pixmap
#         self.setPixmap(result)
#
#
# class LoadingWorker(QThread):
#     """在后台线程中执行AI请求的工作类"""
#     finished = Signal(str)  # 结束信号，携带响应内容
#
#     def __init__(self, ai_function, prompt):
#         super().__init__()
#         self.ai_function = ai_function
#         self.prompt = prompt
#
#     def run(self):
#         """执行AI调用并发送结果"""
#         try:
#             response = self.ai_function(self.prompt)
#             self.finished.emit(response)
#         except Exception as e:
#             print(f"Error in AI request: {str(e)}")
#             self.finished.emit("生成内容时出错")
#
#
# class LoadingScreen(QDialog):
#     """加载屏幕，显示等待AI响应的过程"""
#
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("请稍候")
#         self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
#         self.setModal(True)
#
#         # 创建UI元素
#         layout = QVBoxLayout(self)
#
#         # 加载图片（从指定路径）
#         image_dir = r"D:\source_code\pict"
#
#         # 获取目录中的第一个图片文件
#         image_path = None
#         for file in os.listdir(image_dir):
#             if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
#                 image_path = os.path.join(image_dir, file)
#                 break
#
#         # 如果没有找到图片，使用默认图像
#         if not image_path:
#             self.image_widget = ImageBrightener("")  # 空路径会创建默认图像
#         else:
#             self.image_widget = ImageBrightener(image_path)
#
#         layout.addWidget(self.image_widget, 0, Qt.AlignCenter)
#
#         self.status_label = QLabel("正在生成AI内容，请稍候...", self)
#         self.status_label.setAlignment(Qt.AlignCenter)
#         self.status_label.setFont(QFont("Arial", 10, QFont.Bold))
#         layout.addWidget(self.status_label)
#
#         self.setLayout(layout)
#
#         # 调整对话框大小以适应图片
#         self.adjustSize()
#
#         # 亮度动画 - 增加持续时间让图片亮得更慢
#         self.brightness_animation = QPropertyAnimation(self.image_widget, b"brightness")
#         self.brightness_animation.setDuration(20000)  # 20秒动画，让图片亮得更慢
#         self.brightness_animation.setStartValue(0.0)
#         self.brightness_animation.setEndValue(0.7)  # 先亮到70%
#         self.brightness_animation.setEasingCurve(QEasingCurve.InOutQuad)
#
#         # 最终亮度动画
#         self.final_animation = QPropertyAnimation(self.image_widget, b"brightness")
#         self.final_animation.setDuration(800)  # 稍微延长最终亮度动画
#         self.final_animation.setEndValue(1.0)  # 完全亮
#         self.final_animation.setEasingCurve(QEasingCurve.OutQuad)
#
#         # 存储响应和回调
#         self._response = None
#         self.callback = None
#         self.close_timer = QTimer(self)
#         self.close_timer.setSingleShot(True)
#         self.close_timer.timeout.connect(self.execute_callback)
#
#     def execute_callback(self):
#         """在窗口关闭后执行回调"""
#         self.accept()
#         if self.callback and self._response:
#             self.callback(self._response)
#
#     def start_loading(self, ai_function, prompt, callback):
#         """
#         开始加载过程
#
#         Args:
#             ai_function: 调用AI的函数 (get_LLM_response 或 get_AI_response)
#             prompt: 要发送给AI的提示文本
#             callback: 完成后的回调函数
#         """
#         # 保存回调函数引用
#         self.callback = callback
#
#         # 创建工作线程
#         self.worker = LoadingWorker(ai_function, prompt)
#         self.worker.finished.connect(self._on_ai_response)
#
#         # 启动亮度动画
#         self.brightness_animation.start()
#
#         # 显示对话框并启动工作线程
#         self.worker.start()
#         self.exec()
#
#     def _on_ai_response(self, response):
#         """AI响应完成后完成亮度动画并关闭对话框"""
#         # 保存响应，以便在关闭后执行回调
#         self._response = response
#
#         # 显示状态文本
#         self.status_label.setText("生成完成，正在处理...")
#
#         # 停止当前动画并启动最终亮度动���
#         self.brightness_animation.stop()
#         self.final_animation.setStartValue(self.image_widget.brightness)
#         self.final_animation.start()
#
#         # 设置计时器在动画完成后关闭窗口并执行回调
#         self.close_timer.start(1000)  # 给动画一点额外时间完成


# fresh.py
'''
加载页面代码，显示等待AI响应的过程

-- wy 2025-02-26
'''

import sys
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel)
from PySide6.QtCore import Qt, Signal, QThread, QPropertyAnimation, QEasingCurve, Property, QTimer
from PySide6.QtGui import QPixmap, QPainter, QColor, QLinearGradient, QBrush, QFont


class ImageBrightener(QLabel):
    """自定义widget，显示图片并从底部逐渐变亮"""

    def __init__(self, image_path, parent=None):
        super().__init__(parent)

        # 加载图片
        self.original_pixmap = QPixmap(image_path)
        if self.original_pixmap.isNull():
            # 如果无法加载图片，���建一个默认的灰色图片
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
        # 创建绘图
        result = QPixmap(self.original_pixmap.size())
        result.fill(Qt.transparent)

        painter = QPainter(result)

        # 创建渐变遮罩 - 底部亮，顶部暗
        gradient = QLinearGradient(0, 0, 0, self.height())

        # 计算亮度分界点位置
        boundary = (1.0 - self._brightness) * self.height()

        gradient.setColorAt(0, QColor(255, 255, 255, 0))  # 顶部完全透明
        gradient.setColorAt(boundary / self.height(), QColor(255, 255, 255, 0))  # 分界点完全透明
        gradient.setColorAt(min(1.0, boundary / self.height() + 0.05), QColor(255, 255, 255, 255))  # 分界点下方完全不透明
        gradient.setColorAt(1, QColor(255, 255, 255, 255))  # 底部完全不透明

        # 绘制原始图片
        painter.drawPixmap(0, 0, self.original_pixmap)

        # 使用渐变作为遮罩
        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.fillRect(result.rect(), QBrush(gradient))

        painter.end()

        # 设置pixmap
        self.setPixmap(result)


class LoadingWorker(QThread):
    """在后台线程中执行AI请求的工作类"""
    finished = Signal(str)  # 结束信号，携带响应内容

    def __init__(self, ai_function, prompt):
        super().__init__()
        self.ai_function = ai_function
        self.prompt = prompt

    def run(self):
        """执行AI调用并发送结果"""
        try:
            response = self.ai_function(self.prompt)
            self.finished.emit(response)
        except Exception as e:
            print(f"Error in AI request: {str(e)}")
            self.finished.emit("生成内容时出错")


class LoadingScreen(QDialog):
    """加载屏幕，显示等待AI响应的过程"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("请稍候")
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setModal(True)

        # 保存父窗口引用
        self.input_page = parent

        # 创建UI元素
        layout = QVBoxLayout(self)

        # 加载图片（从指定路径）
        image_dir = r"pict"

        # 获取目录中的第一个图片文件
        image_path = None
        for file in os.listdir(image_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image_path = os.path.join(image_dir, file)
                break

        # 如果没有找到图片，使用默认图像
        if not image_path:
            self.image_widget = ImageBrightener("")  # 空路径会创建默认图像
        else:
            self.image_widget = ImageBrightener(image_path)

        layout.addWidget(self.image_widget, 0, Qt.AlignCenter)

        self.status_label = QLabel("正在生成AI内容，请稍候...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # 调整对话框大小以适应图片
        self.adjustSize()

        # 亮度动画 - 增加持续时间让图片亮得更慢
        self.brightness_animation = QPropertyAnimation(self.image_widget, b"brightness")
        self.brightness_animation.setDuration(20000)  # 20秒动画，让图片亮得更慢
        self.brightness_animation.setStartValue(0.0)
        self.brightness_animation.setEndValue(0.7)  # 先亮到70%
        self.brightness_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # 最终亮度动画
        self.final_animation = QPropertyAnimation(self.image_widget, b"brightness")
        self.final_animation.setDuration(1200)  # 延长最终亮度动画
        self.final_animation.setEndValue(1.0)  # 完全亮
        self.final_animation.setEasingCurve(QEasingCurve.OutQuad)

        # 存储响应和回调
        self._response = None
        self.callback = None
        self.close_timer = QTimer(self)
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self.execute_callback)

    def execute_callback(self):
        """在窗口关闭后执行回调"""
        self.accept()
        if self.callback and self._response:
            self.callback(self._response)

    def start_loading(self, ai_function, prompt, callback, input_page=None):
        """
        开始加载过程

        Args:
            ai_function: 调用AI的函数 (get_LLM_response 或 get_AI_response)
            prompt: 要发送给AI的提示文本
            callback: 完成后的回调函数
            input_page: 输入页面，将在加载时关闭
        """
        # 保存回调函数引用
        self.callback = callback

        # 保存输入页面引用
        if input_page:
            self.input_page = input_page

        # 创建工作线程
        self.worker = LoadingWorker(ai_function, prompt)
        self.worker.finished.connect(self._on_ai_response)

        # 启动亮度动画
        self.brightness_animation.start()

        # 如果提供了输入页面，在显示加载界面前关闭它
        if self.input_page:
            self.input_page.hide()

        # 显示对话框并启动工作线程
        self.worker.start()
        self.show()  # ���用show而不是exec以非模态方式显示
        self.exec()

    def _on_ai_response(self, response):
        """AI响应完成后完成亮度动画并关闭对话框"""
        # 保存响应，以便在关闭后执行回调
        self._response = response



        # 显示状态文本
        self.status_label.setText("生成完成，正在处理...")

        # 停止当前动画并启动最终亮度动画
        self.brightness_animation.stop()
        self.final_animation.setStartValue(self.image_widget.brightness)
        self.final_animation.start()

        # 设置计时器在动画完成后关闭窗口并执行回调
        self.close_timer.start(1500)  # 给动画更多时间完成