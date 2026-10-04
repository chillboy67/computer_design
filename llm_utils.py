"""大模型调用：统一管理客户端、超时和异常"""
import logging
from functools import lru_cache

from zhipuai import ZhipuAI

import config
from prompts import HEALTH_SYSTEM_PROMPT, SPORT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class LLMError(RuntimeError):
    """调用大模型失败，异常信息可以直接展示给用户"""


@lru_cache(maxsize=1)
def _get_client():
    if not config.ZHIPUAI_API_KEY:
        raise LLMError("未配置 ZHIPUAI_API_KEY，请参照 .env.example 在 .env 文件中填写智谱 AI 的 API Key")
    return ZhipuAI(api_key=config.ZHIPUAI_API_KEY, timeout=config.LLM_TIMEOUT, max_retries=2)


def chat(system_prompt, prompt):
    client = _get_client()
    try:
        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
    except Exception as e:
        logger.exception("调用大模型失败")
        raise LLMError(f"AI 服务调用失败，请检查网络和 API Key 后重试。\n\n详细信息：{e}") from e

    content = response.choices[0].message.content if response.choices else ""
    if not content or not content.strip():
        raise LLMError("AI 服务返回了空内容，请稍后重试")
    return content


def get_health_assessment(prompt):
    """生成健康评估报告"""
    return chat(HEALTH_SYSTEM_PROMPT, prompt)


def get_sport_prescription(prompt):
    """生成运动处方"""
    return chat(SPORT_SYSTEM_PROMPT, prompt)
