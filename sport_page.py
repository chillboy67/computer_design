from prompts import SPORT_SECTIONS
from report_page import ReportPage


class SportPrescriptionPage(ReportPage):
    window_title = "运动处方"
    report_title = "运动处方报告"
    sections = SPORT_SECTIONS
