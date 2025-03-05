'''
程序主窗口代码，程序入口

-- wy 2025-02-26
'''
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QStackedWidget, QFormLayout, QMessageBox
from qt_material import apply_stylesheet

from login_window import LoginWindow
from main_window import MainWindow

# 主程序
app = QApplication(sys.argv)
# 应用 Material 主题样式
apply_stylesheet(app, theme='default_light.xml')
window = LoginWindow(MainWindow())
window.setWindowTitle("应用的名称")
# 设置窗口的大小
window.show()

app.exec()