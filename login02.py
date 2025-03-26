from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QCheckBox, QStackedWidget, QMessageBox
)
from PyQt6.QtGui import QFont, QPixmap, QMouseEvent
from PyQt6.QtCore import Qt, QPoint
import sys

class MedicalLoginUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("智能医疗健康系统")
        self.setGeometry(100, 100, 800, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # **无边框**
        self.setStyleSheet("background-color: white; border-radius: 20px;")  # **白色背景**

        self.old_pos = None  # 记录鼠标拖动位置
        self.initUI()

    def initUI(self):
        """ 创建 UI 界面 """

        # **自定义标题栏（最小化 & 关闭按钮）**
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(5, 5, 5, 5)

        title_placeholder = QLabel("智能医疗健康系统")
        title_placeholder.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_placeholder.setStyleSheet("color: #333;")
        title_placeholder.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.minimize_button = QPushButton("—")
        self.minimize_button.setFixedSize(30, 20)
        self.minimize_button.setStyleSheet(self.title_button_style())
        self.minimize_button.clicked.connect(self.showMinimized)

        self.close_button = QPushButton("✕")
        self.close_button.setFixedSize(30, 20)
        self.close_button.setStyleSheet(self.title_button_style())
        self.close_button.clicked.connect(self.close)

        title_bar.addWidget(title_placeholder)
        title_bar.addStretch()
        title_bar.addWidget(self.minimize_button)
        title_bar.addWidget(self.close_button)

        # **主布局**
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # **左侧背景区域**
        left_frame = QLabel(self)
        left_frame.setPixmap(QPixmap("C:\\Users\\MiKu\\Desktop\\pythonProject\\R-C.jpg").scaled(400, 480, Qt.AspectRatioMode.KeepAspectRatioByExpanding))
        left_frame.setScaledContents(True)  # 允许图片根据 QLabel 大小缩放
        left_frame.setFixedSize(400, 480)
        left_frame.setStyleSheet("border-top-left-radius: 20px; border-bottom-left-radius: 20px;")

        # **右侧登录/注册框**
        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.setFixedSize(360, 420)

        self.login_page = self.create_login_page()
        self.register_page = self.create_register_page()

        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.register_page)

        # **左右布局**
        content_layout = QHBoxLayout()
        content_layout.addWidget(left_frame)
        content_layout.addWidget(self.stacked_widget)

        # **添加到主布局**
        main_layout.addLayout(title_bar)  # **标题栏放在顶部**
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def create_login_page(self):
        """ 创建登录界面 """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("登录")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setFont(QFont("Arial", 12))
        self.username_input.setStyleSheet(self.input_style())

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFont(QFont("Arial", 12))
        self.password_input.setStyleSheet(self.input_style())

        remember_me = QCheckBox("记住密码")
        login_btn = QPushButton("登录")
        login_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        login_btn.setStyleSheet(self.button_style())
        login_btn.clicked.connect(self.check_credentials)

        register_btn = QPushButton("没有账号？注册")
        register_btn.setFont(QFont("Arial", 10))
        register_btn.setStyleSheet("background: none; color: #0277BD; border: none;")
        register_btn.clicked.connect(self.show_register_page)

        layout.addWidget(title)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(remember_me)
        layout.addWidget(login_btn)
        layout.addWidget(register_btn)
        widget.setLayout(layout)
        return widget

    def create_register_page(self):
        """ 创建注册界面 """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("注册")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        username = QLineEdit()
        username.setPlaceholderText("请输入用户名")
        username.setStyleSheet(self.input_style())

        email = QLineEdit()
        email.setPlaceholderText("请输入邮箱")
        email.setStyleSheet(self.input_style())

        password = QLineEdit()
        password.setPlaceholderText("请输入密码")
        password.setEchoMode(QLineEdit.EchoMode.Password)
        password.setStyleSheet(self.input_style())

        register_btn = QPushButton("注册")
        register_btn.setStyleSheet(self.button_style())

        back_btn = QPushButton("返回登录")
        back_btn.setStyleSheet("background: none; color: #0277BD; border: none;")
        back_btn.clicked.connect(self.show_login_page)

        layout.addWidget(title)
        layout.addWidget(username)
        layout.addWidget(email)
        layout.addWidget(password)
        layout.addWidget(register_btn)
        layout.addWidget(back_btn)
        widget.setLayout(layout)
        return widget

    def show_register_page(self):
        """ 切换到注册界面 """
        self.stacked_widget.setCurrentIndex(1)

    def show_login_page(self):
        """ 切换回登录界面 """
        self.stacked_widget.setCurrentIndex(0)

    def input_style(self):
        """ 圆角输入框样式 """
        return """
            QLineEdit {
                padding: 10px;
                border-radius: 8px;
                border: 2px solid #B0BEC5;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #0277BD;
            }
        """

    def button_style(self):
        """ 圆角按钮样式 """
        return """
            QPushButton {
                background-color: #0277BD;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #01579B;
            }
        """

    def title_button_style(self):
        """ 自定义标题栏按钮样式 """
        return """
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                color: red;
            }
        """

    def check_credentials(self):
        """ 检查登录凭据 """
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "admin" and password == "123":
            QMessageBox.information(self, "登录成功", "欢迎使用智能医疗健康系统！")
        else:
            QMessageBox.warning(self, "错误", "用户名或密码错误")

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.old_pos and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.old_pos = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MedicalLoginUI()
    window.show()
    sys.exit(app.exec())
