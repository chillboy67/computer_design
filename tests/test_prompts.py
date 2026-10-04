import pytest

from prompts import (BASIC_FIELDS, CLINICAL_FIELDS, HEALTH_SECTIONS, SPORT_SECTIONS,
                     build_health_prompt, build_sport_prompt, calc_bmi,
                     check_consistency, parse_field, split_sections)

FIELDS = {field.key: field for field in BASIC_FIELDS + CLINICAL_FIELDS}


def test_parse_field():
    assert parse_field(FIELDS["height"], " 175.5 ") == 175.5
    assert parse_field(FIELDS["glucose"], "") is None
    with pytest.raises(ValueError, match="请填写年龄"):
        parse_field(FIELDS["age"], "")
    with pytest.raises(ValueError, match="必须是数字"):
        parse_field(FIELDS["weight"], "abc")
    with pytest.raises(ValueError, match="之间"):
        parse_field(FIELDS["sbp"], "500")


def test_check_consistency():
    check_consistency({"sbp": 120, "dbp": 80})
    check_consistency({"sbp": 120, "dbp": None})
    with pytest.raises(ValueError):
        check_consistency({"sbp": 80, "dbp": 120})


def test_calc_bmi():
    assert calc_bmi(175, 70) == 22.9
    assert calc_bmi(None, 70) is None


def test_build_prompts():
    data = {"gender": "男", "age": 30, "height": 175, "weight": 70, "sbp": 120, "dbp": 80}
    health = build_health_prompt(data)
    assert "年龄：30 岁" in health
    assert "BMI：22.9" in health
    assert "收缩压(高压)：120 mmHg" in health
    assert "空腹血糖：未提供" in health
    assert "运动强度" in build_sport_prompt(data)


def test_split_markdown_headings():
    text = (
        "以下是您的运动处方：\n\n"
        "## 运动项目\n快走、游泳\n\n"
        "## 运动频率\n每周 3-5 次\n\n"
        "## 运动强度\n心率 110-130 次/分钟\n\n"
        "## 注意事项\n循序渐进\n\n"
        "## 总结\n坚持锻炼"
    )
    sections = split_sections(text, SPORT_SECTIONS)
    assert sections == {
        "运动项目": "快走、游泳",
        "运动频率": "每周 3-5 次",
        "运动强度": "心率 110-130 次/分钟",
        "注意事项": "循序渐进",
    }


def test_split_numbered_and_bold_headings():
    text = (
        "1. **心血管健康评估**：血压正常\n"
        "   心率偏快\n"
        "2. **糖脂代谢**\n"
        "血糖正常\n"
        "3、体成分\n"
        "BMI 正常"
    )
    sections = split_sections(text, HEALTH_SECTIONS)
    assert sections["心血管健康"] == "血压正常\n   心率偏快"
    assert sections["糖脂代谢"] == "血糖正常"
    assert sections["体成分"] == "BMI 正常"


def test_split_ignores_titles_inside_sentences():
    text = "## 运动项目\n快走\n运动强度应循序渐进地增加\n## 运动强度\n中等强度"
    sections = split_sections(text, SPORT_SECTIONS)
    assert sections["运动项目"] == "快走\n运动强度应循序渐进地增加"
    assert sections["运动强度"] == "中等强度"


def test_split_without_headings():
    assert split_sections("这是一段没有标题的回答", HEALTH_SECTIONS) == {}
    assert split_sections("", HEALTH_SECTIONS) == {}
