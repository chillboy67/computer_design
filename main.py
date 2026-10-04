import logging
import sys

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

import config
from db_utils import init_db
from login03 import MedicalLoginUI
from main_window import MainWindow


def self_check(app):
    """创建各主要窗口后自动退出，用于确认打包后的程序完整可用（python main.py --self-check）"""
    from fresh import LoadingScreen
    from health_page import HealthAssessmentPage
    from history_page import HistoryPage

    windows = [
        MainWindow(username="self-check"),
        HistoryPage("self-check"),
        HealthAssessmentPage("## 心血管健康\n\n自检"),
        LoadingScreen(),
    ]
    for window in windows:
        window.show()
    logging.info("自检通过")
    QTimer.singleShot(500, app.quit)
    return windows


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    init_db()  # 初始化数据库

    # 只创建一个 QApplication 实例
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(config.APP_ICON)))

    # 应用 Material 主题样式
    apply_stylesheet(app, theme="default_light.xml")

    # 创建并显示登录窗口
    window = MedicalLoginUI(MainWindow)
    window.setWindowTitle("健康管理系统")
    window.resize(800, 600)
    window.show()

    if "--self-check" in sys.argv:
        windows = self_check(app)  # noqa: F841  保持窗口引用直到退出

    # 启动事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
