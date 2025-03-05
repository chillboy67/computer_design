'''
登录页面代码，实现简单的登录功能

-- wy 2025-02-26
'''

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QStackedWidget, \
    QFormLayout, QMessageBox


class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()

        # 设置窗口标题
        self.setWindowTitle("登录")

        # 创建布局
        layout = QVBoxLayout()

        # 创建用户名输入框
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("请输入用户名")

        # 创建密码输入框
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("请输入密码")

        # 创建登录按钮
        self.login_button = QPushButton("登录", self)
        self.login_button.clicked.connect(self.check_credentials)

        self.main_window = main_window

        # 添加控件到布局
        layout.addWidget(QLabel("用户名:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("密码:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        # 设置页面布局
        self.setLayout(layout)

    def check_credentials(self):
        # 进行验证
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "admin" and password == "123":
            self.accept_login()
        else:
            # 若输入错误
            self.username_input.clear()
            self.password_input.clear()
            self.username_input.setFocus()

            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)  # 设置图标为警告
            msg_box.setWindowTitle("错误")  # 设置窗口标题
            msg_box.setText("用户名或密码错误")  # 设置消息框的文本内容
            msg_box.setStandardButtons(QMessageBox.Ok)  # 设置按钮
            msg_box.exec()  # 显示消息框

    def accept_login(self):
        self.close()
        # self.main_window = main_window
        self.main_window.show()
        # 登录成功，切换到主界面
        # self.parent().resize(800, 600)
        # self.parent().setCurrentIndex(1)


'''
import sys
# 创建应用并运行
app = QApplication(sys.argv)
window = LoginPage()
window.show()
sys.exit(app.exec())
'''
