import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QLineEdit, QPushButton, QGroupBox,
                              QFormLayout, QComboBox, QScrollArea)
from PySide6.QtCore import Qt

from llm_utils import get_LLM_response
from ai_for_halthy import get_AI_response
from sport_page import SportPrescriptionPage
from health_page import HealthAssessmentPage
from fresh import LoadingScreen


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("健康信息输入")
        self.resize(500, 700)  # 调整窗口大小，专注于输入表单

        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建滚动区域以容纳所有输入字段
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_form = QFormLayout()

        # 性别选择
        self.gender_input = QComboBox()
        self.gender_input.addItems(["男", "女"])
        basic_form.addRow("性别:", self.gender_input)

        # 年龄、身高、体重
        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("岁")
        basic_form.addRow("年龄:", self.age_input)

        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("厘米")
        basic_form.addRow("身高:", self.height_input)

        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("公斤")
        basic_form.addRow("体重:", self.weight_input)

        basic_group.setLayout(basic_form)
        scroll_layout.addWidget(basic_group)

        # 临床数据组
        clinical_group = QGroupBox("临床数据")
        clinical_form = QFormLayout()

        # 体成分数据
        self.body_fat_input = QLineEdit()
        self.body_fat_input.setPlaceholderText("%")
        clinical_form.addRow("体脂率:", self.body_fat_input)

        self.muscle_mass_input = QLineEdit()
        self.muscle_mass_input.setPlaceholderText("公斤")
        clinical_form.addRow("肌肉量:", self.muscle_mass_input)

        self.waist_input = QLineEdit()
        self.waist_input.setPlaceholderText("厘米")
        clinical_form.addRow("腰围:", self.waist_input)

        # 心血管数据
        self.SBP_input = QLineEdit()
        self.SBP_input.setPlaceholderText("mmHg")
        clinical_form.addRow("收缩压(高压):", self.SBP_input)

        self.DBP_input = QLineEdit()
        self.DBP_input.setPlaceholderText("mmHg")
        clinical_form.addRow("舒张压(低压):", self.DBP_input)

        self.heart_rate_input = QLineEdit()
        self.heart_rate_input.setPlaceholderText("次/分钟")
        clinical_form.addRow("心率:", self.heart_rate_input)

        # 代谢数据
        self.glucose_input = QLineEdit()
        self.glucose_input.setPlaceholderText("mmol/L")
        clinical_form.addRow("血糖:", self.glucose_input)

        self.triglycerides_input = QLineEdit()
        self.triglycerides_input.setPlaceholderText("mmol/L")
        clinical_form.addRow("甘油三酯:", self.triglycerides_input)

        clinical_group.setLayout(clinical_form)
        scroll_layout.addWidget(clinical_group)

        # 设置滚动区域内容
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # 底部按钮区域
        button_layout = QHBoxLayout()

        # 运动处方按钮
        self.sport_button = QPushButton("运动处方")
        self.sport_button.setMinimumHeight(40)
        self.sport_button.clicked.connect(self.open_sport_prescription)
        button_layout.addWidget(self.sport_button)

        # 健康评估按钮
        self.health_button = QPushButton("健康评估")
        self.health_button.setMinimumHeight(40)
        self.health_button.clicked.connect(self.open_health_assessment)
        button_layout.addWidget(self.health_button)

        main_layout.addLayout(button_layout)

    def get_user_data(self):
        """收集用户输入的所有健康数据"""
        data = {
            "gender": self.gender_input.currentText(),
            "age": self.age_input.text(),
            "height": self.height_input.text(),
            "weight": self.weight_input.text(),
            "body_fat": self.body_fat_input.text(),
            "muscle_mass": self.muscle_mass_input.text(),
            "waist": self.waist_input.text(),
            "sbp": self.SBP_input.text(),
            "dbp": self.DBP_input.text(),
            "heart_rate": self.heart_rate_input.text(),
            "glucose": self.glucose_input.text(),
            "triglycerides": self.triglycerides_input.text()
        }
        return data

    def open_sport_prescription(self):
        """打开运动处方页面"""
        data = self.get_user_data()

        # 构建提示信息
        prompt = f"""
        请为一位{data['gender']}性患者设计运动处方。患者基本信息：
        - 年龄：{data['age']}岁
        - 身高：{data['height']}厘米
        - 体重：{data['weight']}公斤
        - 体脂率：{data['body_fat']}%
        - 肌肉量：{data['muscle_mass']}公斤
        - 腰围：{data['waist']}厘米
        
        临床指标：
        - 血压：{data['sbp']}/{data['dbp']} mmHg
        - 心率：{data['heart_rate']}次/分钟
        - 血糖：{data['glucose']} mmol/L
        - 甘油三酯：{data['triglycerides']} mmol/L
        
        请详细设计运动处方，包括以下内容：
        1. 运动项目：最适合的2-3种运动模式
        2. 运动频率：每周锻炼次数
        3. 运动强度：以心率百分比表示
        4. 注意事项：根据患者情况提供针对性建议
        """

        # 启动加载屏幕获取AI响应
        self.loading_screen = LoadingScreen(self)
        self.loading_screen.start_loading(
            get_LLM_response,
            prompt,
            self.on_sport_response_ready
        )

    def on_sport_response_ready(self, response):
        """当运动处方响应准备好时调用"""
        self.sport_window = SportPrescriptionPage(response)
        self.sport_window.show()

    def open_health_assessment(self):
        """打开健康评估页面"""
        data = self.get_user_data()

        # 构建提示信息
        prompt = f"""
        请对一位{data['gender']}性患者进行健康评估。患者基本信息：
        - 年龄：{data['age']}岁
        - 身高：{data['height']}厘米
        - 体重：{data['weight']}公斤
        - 体脂率：{data['body_fat']}%
        - 肌肉量：{data['muscle_mass']}公斤
        - 腰围：{data['waist']}厘米
        
        临床指标：
        - 血压：{data['sbp']}/{data['dbp']} mmHg
        - 心率：{data['heart_rate']}次/分钟
        - 血糖：{data['glucose']} mmol/L
        - 甘油三酯：{data['triglycerides']} mmol/L
        
        请进行全面健康评估，包括以下三个方面：
        1. 心血管健康：评估血压和心率状况
        2. 糖脂代谢：评估血糖和血脂状况
        3. 体成分：评估BMI、体脂率、肌肉量等指标
        
        请针对每个方面提供具体评估结果和改善建议。
        """

        # 启动加载屏幕获取AI响应
        self.loading_screen = LoadingScreen(self)
        self.loading_screen.start_loading(
            get_AI_response,
            prompt,
            self.on_health_response_ready
        )

    def on_health_response_ready(self, response):
        """当健康评估响应准备好时调用"""
        self.health_window = HealthAssessmentPage(response)
        self.health_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())