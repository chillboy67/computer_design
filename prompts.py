"""与大模型交互的约定：输入字段定义、提示词构造，以及对返回内容的拆分"""
import re
from dataclasses import dataclass
from typing import Dict, Optional, Sequence


@dataclass(frozen=True)
class Field:
    key: str
    label: str
    unit: str
    minimum: float
    maximum: float
    decimals: int = 1
    required: bool = False


BASIC_FIELDS = (
    Field("age", "年龄", "岁", 1, 120, 0, required=True),
    Field("height", "身高", "厘米", 50, 250, 1, required=True),
    Field("weight", "体重", "公斤", 10, 300, 1, required=True),
)

CLINICAL_FIELDS = (
    Field("body_fat", "体脂率", "%", 1, 70),
    Field("muscle_mass", "肌肉量", "公斤", 5, 150),
    Field("waist", "腰围", "厘米", 30, 200),
    Field("sbp", "收缩压(高压)", "mmHg", 60, 260, 0),
    Field("dbp", "舒张压(低压)", "mmHg", 30, 160, 0),
    Field("heart_rate", "静息心率", "次/分钟", 30, 220, 0),
    Field("glucose", "空腹血糖", "mmol/L", 1, 35),
    Field("triglycerides", "甘油三酯", "mmol/L", 0.1, 30, 2),
)

HEALTH_SECTIONS = ("心血管健康", "糖脂代谢", "体成分")
SPORT_SECTIONS = ("运动项目", "运动频率", "运动强度", "注意事项")


def _headings(sections):
    return "\n".join(f"## {title}" for title in sections)


HEALTH_SYSTEM_PROMPT = f"""你是一名资深的临床医学与健康管理专家，熟悉国内外权威指南和 PubMed 上的循证医学证据。你的任务是根据用户提供的体检数据，给出个性化的健康评估。

输出要求：
1. 使用 Markdown 格式，必须使用以下二级标题，并按此顺序组织内容：
{_headings(HEALTH_SECTIONS)}
2. 每个部分先解读相关指标（给出正常参考范围），再说明风险等级，最后给出具体、可执行的改善建议；
3. 用户未提供的指标请注明“未提供，无法评估”，不要臆测或编造数据；
4. 如发现明显异常或高危指标（例如血压 ≥ 180/110 mmHg、空腹血糖 ≥ 11.1 mmol/L），请明确提示尽快就医。"""

SPORT_SYSTEM_PROMPT = f"""你是一名资深的运动医学专家，熟悉 ACSM 运动处方指南和 PubMed 上的循证医学证据。你的任务是根据用户提供的体检数据，按照 FITT 原则制定个性化运动处方。

输出要求：
1. 使用 Markdown 格式，必须使用以下二级标题，并按此顺序组织内容：
{_headings(SPORT_SECTIONS)}
2. 运动项目：推荐 2-3 种最适合的运动方式并说明理由；运动频率：每周次数及每次时长；运动强度：结合用户年龄和静息心率，计算出具体的目标心率区间，并给出对应的主观疲劳度（RPE）；注意事项：结合用户的异常指标给出禁忌与风险提示；
3. 用户未提供的指标不要臆测或编造数据；
4. 如指标提示运动风险较高（例如血压 ≥ 160/100 mmHg），请提示先进行医学评估，再开始中高强度运动。"""


def format_number(value) -> str:
    return f"{value:g}"


def parse_field(field: Field, text: str) -> Optional[float]:
    """把输入框中的文本转换为数值，不合法时抛出带提示信息的 ValueError"""
    text = text.strip()
    if not text:
        if field.required:
            raise ValueError(f"请填写{field.label}")
        return None
    try:
        value = float(text)
    except ValueError:
        raise ValueError(f"{field.label}必须是数字") from None
    if not field.minimum <= value <= field.maximum:
        raise ValueError(
            f"{field.label}应在 {format_number(field.minimum)}~{format_number(field.maximum)} {field.unit} 之间"
        )
    return value


def check_consistency(data: Dict) -> None:
    """检查多个字段之间的逻辑关系"""
    sbp, dbp = data.get("sbp"), data.get("dbp")
    if sbp is not None and dbp is not None and sbp <= dbp:
        raise ValueError("收缩压应高于舒张压，请检查血压数据")


def calc_bmi(height_cm, weight_kg) -> Optional[float]:
    if not height_cm or not weight_kg:
        return None
    return round(weight_kg / (height_cm / 100) ** 2, 1)


def _profile_line(field: Field, value) -> str:
    if value is None:
        return f"- {field.label}：未提供"
    return f"- {field.label}：{format_number(value)} {field.unit}"


def build_profile(data: Dict) -> str:
    """把用户数据整理成提示词中的“患者信息”部分"""
    lines = ["基本信息：", f"- 性别：{data.get('gender') or '未提供'}"]
    lines += [_profile_line(field, data.get(field.key)) for field in BASIC_FIELDS]
    bmi = calc_bmi(data.get("height"), data.get("weight"))
    if bmi is not None:
        lines.append(f"- BMI：{format_number(bmi)} kg/m²")
    lines += ["", "临床指标："]
    lines += [_profile_line(field, data.get(field.key)) for field in CLINICAL_FIELDS]
    return "\n".join(lines)


def build_health_prompt(data: Dict) -> str:
    return (
        "请根据以下体检数据进行全面的健康评估。\n\n"
        f"{build_profile(data)}\n\n"
        "请分别评估心血管健康（血压、心率）、糖脂代谢（血糖、血脂）和体成分（BMI、体脂率、肌肉量、腰围），"
        "并针对每个方面给出具体的评估结果和改善建议。"
    )


def build_sport_prompt(data: Dict) -> str:
    return (
        "请根据以下体检数据制定个性化运动处方。\n\n"
        f"{build_profile(data)}\n\n"
        "请详细给出运动项目、运动频率、运动强度和注意事项。"
    )


_MARKDOWN_HEADING = re.compile(r"^\s*(#{1,6})\s")
_TITLE_SUFFIXES = "评估|分析|状况|情况|建议|方面"


def split_sections(text: str, titles: Sequence[str]) -> Dict[str, str]:
    """按标题把 AI 返回的 Markdown 拆分成若干部分，返回 {标题: 内容}，未找到的标题不在结果中

    优先识别 “## 标题” 形式；模型没有按要求输出时，再识别 “1. 标题”、“**标题**：” 等常见写法。
    """
    if not text or not titles:
        return {}
    alternatives = "|".join(re.escape(title) for title in sorted(titles, key=len, reverse=True))
    pattern = re.compile(
        r"^\s*(?P<hashes>#{1,6})?\s*"
        r"(?P<number>(?:[（(]?\d{1,2}[.、)）]|[一二三四五六七八九十]{1,2}[、.])\s*)?"
        r"(?P<bold>\*\*)?\s*"
        rf"(?P<title>{alternatives})(?:{_TITLE_SUFFIXES})?"
        r"\s*(?:\*\*)?\s*[:：]?\s*(?:\*\*)?\s*(?P<rest>.*)$"
    )

    lines = text.splitlines()
    candidates = []  # (行号, 标题, 标题行剩余内容, Markdown 标题级别)
    for index, line in enumerate(lines):
        match = pattern.match(line)
        if not match:
            continue
        level = len(match["hashes"] or "")
        rest = match["rest"].strip()
        if level or match["number"] or match["bold"] or not rest:
            candidates.append((index, match["title"], rest, level))

    if any(level for *_, level in candidates):
        candidates = [candidate for candidate in candidates if candidate[3]]

    headings, seen = [], set()
    for candidate in candidates:
        if candidate[1] not in seen:
            seen.add(candidate[1])
            headings.append(candidate)

    sections = {}
    for i, (index, title, rest, level) in enumerate(headings):
        end = headings[i + 1][0] if i + 1 < len(headings) else len(lines)
        if level:  # 遇到同级或更高级的其他标题（如“## 总结”）时结束当前部分
            for j in range(index + 1, end):
                heading = _MARKDOWN_HEADING.match(lines[j])
                if heading and len(heading.group(1)) <= level:
                    end = j
                    break
        body = ([rest] if rest else []) + lines[index + 1:end]
        sections[title] = "\n".join(body).strip()
    return sections
