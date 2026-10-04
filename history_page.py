"""历史记录：查看、删除过去的评估，并以折线图展示各项指标的变化趋势"""
from PySide6.QtCharts import QChart, QChartView, QDateTimeAxis, QLineSeries, QValueAxis
from PySide6.QtCore import QDateTime, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (QAbstractItemView, QComboBox, QHBoxLayout,
                               QHeaderView, QLabel, QMessageBox, QPushButton,
                               QSplitter, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)

from health_page import HealthAssessmentPage
from prompts import format_number
from record_service import RECORD_TYPES, RecordService, trend_points
from sport_page import SportPrescriptionPage

REPORT_PAGES = {"health": HealthAssessmentPage, "sport": SportPrescriptionPage}

# 趋势图可选指标：(名称, [(字段, 图例)], 单位, [(参考值, 说明)])
TREND_METRICS = (
    ("体重", [("weight", "体重")], "公斤", []),
    ("BMI", [("bmi", "BMI")], "kg/m²", [(18.5, "偏瘦线 18.5"), (24, "超重线 24")]),
    ("血压", [("sbp", "收缩压"), ("dbp", "舒张压")], "mmHg", [(140, "收缩压上限 140"), (90, "舒张压上限 90")]),
    ("静息心率", [("heart_rate", "静息心率")], "次/分钟", [(60, "下限 60"), (100, "上限 100")]),
    ("空腹血糖", [("glucose", "空腹血糖")], "mmol/L", [(6.1, "正常上限 6.1")]),
    ("甘油三酯", [("triglycerides", "甘油三酯")], "mmol/L", [(1.7, "正常上限 1.7")]),
    ("体脂率", [("body_fat", "体脂率")], "%", []),
    ("腰围", [("waist", "腰围")], "厘米", []),
    ("肌肉量", [("muscle_mass", "肌肉量")], "公斤", []),
)

TABLE_COLUMNS = ("时间", "类型", "体重", "BMI", "血压", "静息心率", "空腹血糖", "甘油三酯")


def _fmt(value):
    return "-" if value is None else format_number(value)


def _msecs(when):
    return int(when.timestamp() * 1000)


def _datetime(msecs):
    return QDateTime.fromMSecsSinceEpoch(msecs)


class HistoryPage(QWidget):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.records = []
        self.report_windows = []
        self.setWindowTitle(f"历史记录 - {username}")
        self.resize(920, 700)
        self.init_ui()
        self.reload()

    def init_ui(self):
        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Vertical)

        # 上半部分：记录列表
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        self.table = QTableWidget(0, len(TABLE_COLUMNS))
        self.table.setHorizontalHeaderLabels(TABLE_COLUMNS)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.doubleClicked.connect(self.view_report)
        table_layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        self.count_label = QLabel()
        view_btn = QPushButton("查看报告")
        view_btn.clicked.connect(self.view_report)
        delete_btn = QPushButton("删除记录")
        delete_btn.clicked.connect(self.delete_record)
        button_layout.addWidget(self.count_label)
        button_layout.addStretch()
        button_layout.addWidget(view_btn)
        button_layout.addWidget(delete_btn)
        table_layout.addLayout(button_layout)
        splitter.addWidget(table_widget)

        # 下半部分：趋势图
        chart_widget = QWidget()
        chart_layout = QVBoxLayout(chart_widget)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        metric_layout = QHBoxLayout()
        metric_layout.addWidget(QLabel("趋势指标:"))
        self.metric_combo = QComboBox()
        self.metric_combo.addItems([metric[0] for metric in TREND_METRICS])
        self.metric_combo.currentIndexChanged.connect(self.update_chart)
        metric_layout.addWidget(self.metric_combo)
        metric_layout.addStretch()
        chart_layout.addLayout(metric_layout)

        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(280)
        chart_layout.addWidget(self.chart_view)
        splitter.addWidget(chart_widget)

        splitter.setSizes([300, 400])
        layout.addWidget(splitter)

    def reload(self):
        """重新读取记录并刷新列表和趋势图"""
        self.records = RecordService.list_records(self.username)
        self.table.setRowCount(len(self.records))
        for row, record in enumerate(self.records):
            blood_pressure = "-"
            if record.sbp is not None and record.dbp is not None:
                blood_pressure = f"{record.sbp}/{record.dbp}"
            values = (
                f"{record.created_at:%Y-%m-%d %H:%M}",
                RECORD_TYPES.get(record.record_type, "-"),
                _fmt(record.weight),
                _fmt(record.bmi),
                blood_pressure,
                _fmt(record.heart_rate),
                _fmt(record.glucose),
                _fmt(record.triglycerides),
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, column, item)
        self.count_label.setText(f"共 {len(self.records)} 条记录")
        self.update_chart()

    def selected_record(self):
        row = self.table.currentRow()
        if 0 <= row < len(self.records) and self.table.selectionModel().hasSelection():
            return self.records[row]
        QMessageBox.information(self, "提示", "请先选择一条记录")
        return None

    def view_report(self):
        record = self.selected_record()
        if not record:
            return
        page_class = REPORT_PAGES.get(record.record_type, HealthAssessmentPage)
        window = page_class(record.report_text, generated_at=record.created_at)
        self.report_windows = [w for w in self.report_windows if w.isVisible()]
        self.report_windows.append(window)
        window.show()

    def delete_record(self):
        record = self.selected_record()
        if not record:
            return
        answer = QMessageBox.question(
            self, "删除记录", f"确定删除 {record.created_at:%Y-%m-%d %H:%M} 的这条记录吗？删除后无法恢复。"
        )
        if answer != QMessageBox.Yes:
            return
        if not RecordService.delete_record(self.username, record.id):
            QMessageBox.warning(self, "错误", "删除失败，请稍后重试")
        self.reload()

    def update_chart(self):
        name, series_specs, unit, references = TREND_METRICS[self.metric_combo.currentIndex()]
        chart = QChart()
        chart.legend().setAlignment(Qt.AlignBottom)

        data_series = []
        for key, label in series_specs:
            points = trend_points(self.records, key)
            if not points:
                continue
            series = QLineSeries()
            series.setName(label)
            series.setPointsVisible(True)
            for when, value in points:
                series.append(_msecs(when), value)
            data_series.append((series, points))

        if not data_series:
            chart.setTitle(f"暂无{name}数据，完成评估后即可查看变化趋势")
            self.chart_view.setChart(chart)
            return
        chart.setTitle(f"{name}变化趋势")

        times = [when for _, points in data_series for when, _ in points]
        values = [value for _, points in data_series for _, value in points]
        x_min, x_max = _msecs(min(times)), _msecs(max(times))
        if x_min == x_max:  # 只有一个时间点时左右各留半天
            x_min, x_max = x_min - 43_200_000, x_max + 43_200_000

        # 只显示与数据范围接近的参考线，避免把曲线压扁
        low, high = min(values), max(values)
        span = max(high - low, abs(high) * 0.3, 1)
        visible_refs = [(v, label) for v, label in references if low - span <= v <= high + span]
        y_values = values + [v for v, _ in visible_refs]
        y_min, y_max = min(y_values), max(y_values)
        padding = max((y_max - y_min) * 0.15, abs(y_max) * 0.05, 0.5)

        axis_x = QDateTimeAxis()
        axis_x.setFormat("MM-dd")
        axis_x.setTickCount(min(max(len(set(times)), 2), 6))
        axis_x.setRange(_datetime(x_min), _datetime(x_max))
        axis_y = QValueAxis()
        axis_y.setTitleText(unit)
        axis_y.setLabelFormat("%.1f")
        axis_y.setRange(y_min - padding, y_max + padding)
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)

        for series, _ in data_series:
            chart.addSeries(series)
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)

        for value, label in visible_refs:
            ref = QLineSeries()
            ref.setName(label)
            ref.append(x_min, value)
            ref.append(x_max, value)
            pen = QPen(QColor("#9E9E9E"))
            pen.setStyle(Qt.DashLine)
            ref.setPen(pen)
            chart.addSeries(ref)
            ref.attachAxis(axis_x)
            ref.attachAxis(axis_y)

        self.chart_view.setChart(chart)
