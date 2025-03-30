'''
程序主窗口代码，程序入口

-- wy 2025-02-26
'''
import sys
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from login03 import MedicalLoginUI
from main_window import MainWindow
from db_utils import init_db

if __name__ == "__main__":
    init_db()  # 初始化数据库

    # 只创建一个 QApplication 实例
    app = QApplication(sys.argv)

    # 创建并显示登录窗口
    window = MedicalLoginUI(MainWindow)
    window.setWindowTitle("健康管理系统")
    window.resize(800, 600)
    window.show()

    # 启动事件循环
    sys.exit(app.exec())