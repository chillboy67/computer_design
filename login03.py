import logging
import sys

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QStackedWidget, QVBoxLayout, QWidget
)

import config
from user_service import MIN_PASSWORD_LENGTH, UserService

logger = logging.getLogger(__name__)

# 勾选“记住密码”后，密码框中显示的占位内容（不是真实密码）
SAVED_PASSWORD_PLACEHOLDER = "********"


class MedicalLoginUI(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window

        # 创建用于存储设置的对象
        self.settings = QSettings("HealthApp", "Login")

        self.setWindowTitle("智能医疗健康系统")
        self.setGeometry(100, 100, 800, 500)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框
        self.setStyleSheet("background-color: white; border-radius: 20px;")  # 白色背景

        self.old_pos = None  # 记录鼠标拖动位置
        self.saved_token = None  # “记住密码”保存的登录令牌
        self.main_window_instance = None
        self.initUI()

        # 加载保存的凭据
        self.load_saved_credentials()

    def initUI(self):
        """ 创建 UI 界面 """

        # 自定义标题栏（最小化 & 关闭按钮）
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(5, 5, 5, 5)

        title_placeholder = QLabel("智能医疗健康系统")
        title_placeholder.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_placeholder.setStyleSheet("color: #333;")
        title_placeholder.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.minimize_button = QPushButton("—")
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setStyleSheet(self.title_button_style())
        self.minimize_button.clicked.connect(self.showMinimized)

        self.close_button = QPushButton("✕")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #e81123;
                color: white;
                border: none;
                font-size: 16px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #f1707a;
            }
        """)
        self.close_button.clicked.connect(self.close)

        title_bar.addWidget(title_placeholder)
        title_bar.addStretch()
        title_bar.addWidget(self.minimize_button)
        title_bar.addWidget(self.close_button)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 左侧图片区域 - 图片不存在时显示提示文字
        left_frame = QLabel(self)
        left_frame.setFixedSize(400, 480)
        left_frame.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(str(config.LOGIN_IMAGE))
        if not pixmap.isNull():
            left_frame.setPixmap(pixmap.scaled(380, 460, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logger.warning("未找到登录图片：%s", config.LOGIN_IMAGE)
            left_frame.setText("图片未找到")
            left_frame.setStyleSheet("background-color: #f0f0f0; color: #666;")

        # 右侧登录/注册框
        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.setFixedSize(360, 480)

        self.login_page = self.create_login_page()
        self.register_page = self.create_register_page()

        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.register_page)

        # 左右布局
        content_layout = QHBoxLayout()
        content_layout.addWidget(left_frame)
        content_layout.addWidget(self.stacked_widget)

        # 添加到主布局
        main_layout.addLayout(title_bar)  # 标题栏放在顶部
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def create_login_page(self):
        """ 创建登录界面 """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(10)  # 减小组件之间的距离

        title = QLabel("登录")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(10)  # 标题和表单之间的距离

        # 用户名输入
        username_label = QLabel("用户名:")
        username_label.setFont(QFont("Arial", 12))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setFont(QFont("Arial", 12))
        self.username_input.setStyleSheet(self.input_style())

        # 密码输入
        password_label = QLabel("密码:")
        password_label.setFont(QFont("Arial", 12))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Arial", 12))
        self.password_input.setStyleSheet(self.input_style())

        # 用户修改输入后，不再使用保存的登录令牌；回车直接登录
        self.username_input.textEdited.connect(self.discard_saved_token)
        self.password_input.textEdited.connect(self.discard_saved_token)
        self.username_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.check_credentials)

        # 紧凑布局
        form_layout = QVBoxLayout()
        form_layout.setSpacing(5)  # 更紧凑的表单元素间距
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        layout.addLayout(form_layout)

        # 记住密码选项
        self.remember_me = QCheckBox("记住密码")
        self.remember_me.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #B0BEC5;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #0277BD;
                border-color: #0277BD;
                image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24"><path fill="white" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/></svg>');
            }
            QCheckBox::indicator:hover {
                border: 2px solid #0277BD;
            }
        """)
        layout.addWidget(self.remember_me)

        # 按钮
        login_btn = QPushButton("登录")
        login_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        login_btn.setStyleSheet(self.button_style())
        login_btn.clicked.connect(self.check_credentials)
        layout.addWidget(login_btn)

        register_btn = QPushButton("没有账号？注册")
        register_btn.setFont(QFont("Arial", 10))
        register_btn.setStyleSheet("background: none; color: #0277BD; border: none;")
        register_btn.clicked.connect(self.show_register_page)
        layout.addWidget(register_btn)

        return widget

    def create_register_page(self):
        """ 创建注册界面 """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(10)  # 减小组件之间的距离

        title = QLabel("注册")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(10)  # 标题和表单之间的距离

        # 紧凑布局
        form_layout = QVBoxLayout()
        form_layout.setSpacing(5)  # 更紧凑的表单元素间距

        # 用户名输入
        username_label = QLabel("用户名:")
        username_label.setFont(QFont("Arial", 12))
        self.reg_username_input = QLineEdit()  # 重命名避免变量覆盖
        self.reg_username_input.setPlaceholderText("2-20 位字母、数字、下划线或汉字")
        self.reg_username_input.setStyleSheet(self.input_style())

        # 邮箱输入
        email_label = QLabel("邮箱:")
        email_label.setFont(QFont("Arial", 12))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("选填")
        self.email_input.setStyleSheet(self.input_style())

        # 密码输入
        password_label = QLabel("密码:")
        password_label.setFont(QFont("Arial", 12))
        self.reg_password_input = QLineEdit()  # 重命名避免变量覆盖
        self.reg_password_input.setPlaceholderText(f"至少 {MIN_PASSWORD_LENGTH} 位")
        self.reg_password_input.setEchoMode(QLineEdit.Password)
        self.reg_password_input.setStyleSheet(self.input_style())

        # 确认密码
        confirm_label = QLabel("确认密码:")
        confirm_label.setFont(QFont("Arial", 12))
        self.reg_confirm_input = QLineEdit()
        self.reg_confirm_input.setPlaceholderText("请再次输入密码")
        self.reg_confirm_input.setEchoMode(QLineEdit.Password)
        self.reg_confirm_input.setStyleSheet(self.input_style())
        self.reg_confirm_input.returnPressed.connect(self.register_user)

        form_layout.addWidget(username_label)
        form_layout.addWidget(self.reg_username_input)
        form_layout.addWidget(email_label)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.reg_password_input)
        form_layout.addWidget(confirm_label)
        form_layout.addWidget(self.reg_confirm_input)
        layout.addLayout(form_layout)

        # 按钮
        register_btn = QPushButton("注册")
        register_btn.setStyleSheet(self.button_style())
        register_btn.clicked.connect(self.register_user)
        layout.addWidget(register_btn)

        back_btn = QPushButton("返回登录")
        back_btn.setStyleSheet("background: none; color: #0277BD; border: none;")
        back_btn.clicked.connect(self.show_login_page)
        layout.addWidget(back_btn)

        return widget

    def load_saved_credentials(self):
        """加载保存的用户名和登录令牌（本地不保存明文密码）"""
        self.settings.remove("password")  # 清理旧版本以明文保存的密码
        username = self.settings.value("username", "")
        token = self.settings.value("remember_token", "")
        if self.settings.value("remember_password", False, type=bool) and username and token:
            self.username_input.setText(username)
            self.password_input.setText(SAVED_PASSWORD_PLACEHOLDER)
            self.remember_me.setChecked(True)
            self.saved_token = token

    def discard_saved_token(self):
        """用户修改了用户名或密码，保存的令牌不再适用"""
        if self.saved_token:
            self.saved_token = None
            if self.password_input.text() == SAVED_PASSWORD_PLACEHOLDER:
                self.password_input.clear()

    def save_credentials(self, username):
        """勾选“记住密码”时保存用户名和新的登录令牌，否则清除"""
        token = UserService.issue_remember_token(username) if self.remember_me.isChecked() else None
        if token:
            self.settings.setValue("username", username)
            self.settings.setValue("remember_token", token)
            self.settings.setValue("remember_password", True)
        else:
            UserService.clear_remember_token(username)
            self.settings.remove("username")
            self.settings.remove("remember_token")
            self.settings.setValue("remember_password", False)

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
                color: #333333;
                background-color: #FFFFFF;
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
                background-color: #0277BD;
                color: white;
                border: none;
                font-size: 16px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #01579B;
            }
        """

    def check_credentials(self):
        """ 检查登录凭据 """
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            QMessageBox.warning(self, "错误", "请输入用户名和密码")
            return

        if self.saved_token:
            authenticated = UserService.verify_remember_token(username, self.saved_token)
            if not authenticated:  # 令牌失效（例如在其他地方重新登录过），需要重新输入密码
                self.discard_saved_token()
                self.password_input.setFocus()
                QMessageBox.warning(self, "错误", "登录信息已过期，请重新输入密码")
                return
        else:
            authenticated = UserService.verify_user(username, password)

        if not authenticated:
            logger.info("用户 %s 登录失败", username)
            QMessageBox.warning(self, "错误", "用户名或密码错误")
            return

        UserService.update_last_login(username)
        self.save_credentials(username)

        QMessageBox.information(self, "登录成功", "欢迎使用智能医疗健康系统！")
        if self.main_window:
            # 处理传入的是类还是实例的情况
            if isinstance(self.main_window, type):
                self.main_window_instance = self.main_window(username=username)
                self.main_window_instance.show()
            else:
                self.main_window.show()
        self.close()  # 登录成功后关闭窗口

    def register_user(self):
        """ 注册新用户 """
        username = self.reg_username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.reg_password_input.text()

        error = UserService.validate_registration(username, email, password)
        if not error and password != self.reg_confirm_input.text():
            error = "两次输入的密码不一致"
        if not error and UserService.user_exists(username):
            error = "用户名已存在"
        if error:
            QMessageBox.warning(self, "错误", error)
            return

        if not UserService.create_user(username, password, email):
            QMessageBox.warning(self, "错误", "注册失败，请稍后重试")
            return

        QMessageBox.information(self, "注册成功", "账号已成功注册，请登录！")
        for line_edit in (self.reg_username_input, self.email_input,
                          self.reg_password_input, self.reg_confirm_input):
            line_edit.clear()
        self.discard_saved_token()
        self.remember_me.setChecked(False)
        self.username_input.setText(username)
        self.password_input.clear()
        self.show_login_page()
        self.password_input.setFocus()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos and event.buttons() == Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None


if __name__ == '__main__':
    from db_utils import init_db
    init_db()
    app = QApplication(sys.argv)
    window = MedicalLoginUI()
    window.show()
    sys.exit(app.exec())