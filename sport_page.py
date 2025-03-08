# sport_page.py
import sys
import re
import markdown
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QMessageBox, QGridLayout, \
    QScrollArea
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


class SportPrescriptionPage(QWidget):
    def __init__(self, response):
        super().__init__()
        self.response = response
        self.initUI()

    def initUI(self):
        self.setWindowTitle('运动处方页面')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #f0f0f0;")

        # 创建主布局
        main_layout = QVBoxLayout()

        # 添加滚动区域以支持内容滚动
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)

        # 内容布局
        content_layout = QGridLayout(scroll_content)
        content_layout.setSpacing(15)

        # 标题
        title_label = QLabel('运动处方')
        title_label.setFont(QFont('楷体', 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title_label, 0, 0, 1, 2)

        # 解析运动建议
        exercise, frequency, intensity = self.parse_response(self.response)

        # 运动项目模块
        self.exercise_label = QLabel('运动项目:')
        self.exercise_label.setFont(QFont('楷体', 14, QFont.Bold))
        self.exercise_display = QTextEdit()
        self.exercise_display.setReadOnly(True)
        self.exercise_display.setHtml(exercise)
        content_layout.addWidget(self.exercise_label, 1, 0)
        content_layout.addWidget(self.exercise_display, 1, 1)

        # 运动频率模块
        self.frequency_label = QLabel('运动频率:')
        self.frequency_label.setFont(QFont('楷体', 14, QFont.Bold))
        self.frequency_display = QTextEdit()
        self.frequency_display.setReadOnly(True)
        self.frequency_display.setHtml(frequency)
        content_layout.addWidget(self.frequency_label, 2, 0)
        content_layout.addWidget(self.frequency_display, 2, 1)

        # 运动强度模块
        self.intensity_label = QLabel('运动强度:')
        self.intensity_label.setFont(QFont('楷体', 14, QFont.Bold))
        self.intensity_display = QTextEdit()
        self.intensity_display.setReadOnly(True)
        self.intensity_display.setHtml(intensity)
        content_layout.addWidget(self.intensity_label, 3, 0)
        content_layout.addWidget(self.intensity_display, 3, 1)

        # 完整响应(隐藏，但保留以备查询)
        self.full_response = self.response

        # 添加滚动区域到主布局
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def parse_response(self, response):
        """解析AI响应并提取相关部分"""
        # 初始化默认空值
        exercise_content = ""
        frequency_content = ""
        intensity_content = ""

        # 第一种方法：查找明确标记的部分
        exercise_pattern = r'(?:运动项目|建议运动|推荐运动|运动类型)[：:]\s*([\s\S]*?)(?:\n\n|\n(?=运动频率|锻炼频率|频率|运动强度|锻炼强度|强度|注意事项|其他建议|建议|$))'
        frequency_pattern = r'(?:运动频率|锻炼频率|频率)[：:]\s*([\s\S]*?)(?:\n\n|\n(?=运动强度|锻炼强度|强度|运动项目|建议运动|推荐运动|注意事项|其他建议|建议|$))'
        intensity_pattern = r'(?:运动强度|锻炼强度|强度)[：:]\s*([\s\S]*?)(?:\n\n|\n(?=运动频率|锻炼频率|频率|运动项目|建议运动|推荐运动|注意事项|其他建议|建议|$))'

        exercise_match = re.search(exercise_pattern, response)
        frequency_match = re.search(frequency_pattern, response)
        intensity_match = re.search(intensity_pattern, response)

        # 检查是否找到了结构化内容
        found_structured = False
        if exercise_match:
            exercise_content = exercise_match.group(1).strip()
            found_structured = True
        if frequency_match:
            frequency_content = frequency_match.group(1).strip()
            found_structured = True
        if intensity_match:
            intensity_content = intensity_match.group(1).strip()
            found_structured = True

        # 如果没有找到结构化内容，尝试按段落分配
        if not found_structured:
            paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]

            # 如果有足够的段落，就按顺序分配
            if paragraphs:
                # 首先检查每个段落，查找关键词来分类
                for paragraph in paragraphs:
                    if any(keyword in paragraph for keyword in
                           ['有氧', '散步', '跑步', '游泳', '慢跑', '健走', '运动项目',
                            '运动类型']) and not exercise_content:
                        exercise_content = paragraph
                    elif any(keyword in paragraph for keyword in
                             ['每周', '每天', '次数', '频率', '运动频率']) and not frequency_content:
                        frequency_content = paragraph
                    elif any(keyword in paragraph for keyword in
                             ['强度', '中等', '剧烈', '运动强度']) and not intensity_content:
                        intensity_content = paragraph

                # 如果分类后仍有空项，按顺序分配剩余段落
                remaining_paragraphs = [p for p in paragraphs if
                                        p not in [exercise_content, frequency_content, intensity_content]]

                if not exercise_content and remaining_paragraphs:
                    exercise_content = remaining_paragraphs.pop(0)
                if not frequency_content and remaining_paragraphs:
                    frequency_content = remaining_paragraphs.pop(0)
                if not intensity_content and remaining_paragraphs:
                    intensity_content = remaining_paragraphs.pop(0)

        # 如果仍然没有内容，尝试基于句子的分配
        if not (exercise_content or frequency_content or intensity_content):
            sentences = [s.strip() + '。' for s in response.split('。') if s.strip()]

            for sentence in sentences:
                if any(keyword in sentence for keyword in ['有氧', '散步', '跑步', '游泳', '慢跑', '健走', '运动项目',
                                                           '运动类型']) and not exercise_content:
                    exercise_content = sentence
                elif any(keyword in sentence for keyword in
                         ['每周', '每天', '次数', '频率', '运动频率']) and not frequency_content:
                    frequency_content = sentence
                elif any(keyword in sentence for keyword in
                         ['强度', '中等', '剧烈', '运动强度']) and not intensity_content:
                    intensity_content = sentence

        # 最后的处理：如果某些部分没有内容，确保有合理的默认值
        if not exercise_content:
            exercise_content = "未找到特定的运动项目推荐，请参考完整评估结果。"

        if not frequency_content:
            frequency_content = "未找到特定的运动频率推荐，请咨询医生获取个性化建议。"

        if not intensity_content:
            intensity_content = "未找到特定的运动强度推荐，请根据自身情况适当调整运动强度。"

        # 转换为HTML格式
        exercise_html = markdown.markdown(exercise_content)
        frequency_html = markdown.markdown(frequency_content)
        intensity_html = markdown.markdown(intensity_content)

        return exercise_html, frequency_html, intensity_html