from prompts import HEALTH_SECTIONS
from report_page import ReportPage


class HealthAssessmentPage(ReportPage):
    window_title = "健康评估"
    report_title = "健康评估报告"
    sections = HEALTH_SECTIONS
