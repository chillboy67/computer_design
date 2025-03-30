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

    # 应用 Material 主题样式
    apply_stylesheet(app, theme='default_light.xml')

    # 创建并显示登录窗口
    window = MedicalLoginUI(MainWindow)
    window.setWindowTitle("健康管理系统")
    window.resize(800, 600)
    window.show()

    # 启动事件循环
    sys.exit(app.exec())