"""大模型调用：统一管理客户端、超时和异常，支持流式输出"""
import logging
from functools import lru_cache

from zhipuai import ZhipuAI
from zhipuai.core import NOT_GIVEN

import config
from prompts import HEALTH_SYSTEM_PROMPT, SPORT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class LLMError(RuntimeError):
    """调用大模型失败，异常信息可以直接展示给用户"""


@lru_cache(maxsize=1)
def _get_client():
    if not config.LLM_API_KEY:
        raise LLMError("未配置 LLM_API_KEY，请参照 .env.example 在 .env 文件中填写大模型服务的 API Key")
    return ZhipuAI(
        api_key=config.LLM_API_KEY,
        base_url=config.LLM_BASE_URL,
        timeout=config.LLM_TIMEOUT,
        max_retries=2,
    )


def stream_chat(system_prompt, prompt):
    """流式调用大模型，逐段返回生成的文本（生成器）"""
    client = _get_client()
    try:
        stream = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            stream=True,
            # SDK 默认会带上值为 null 的智谱专有参数，部分 OpenAI 兼容服务不接受，这里不发送
            response_format=NOT_GIVEN,
            thinking=NOT_GIVEN,
        )
    except Exception as e:
        logger.exception("调用大模型失败")
        raise LLMError(f"AI 服务调用失败，请检查网络和 API Key 后重试。\n\n详细信息：{e}") from e

    try:
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        logger.exception("读取大模型输出失败")
        raise LLMError(f"AI 服务连接中断，请稍后重试。\n\n详细信息：{e}") from e
    finally:
        stream.response.close()  # 提前停止时及时断开连接


def chat(system_prompt, prompt):
    """非流式调用，返回完整文本"""
    content = "".join(stream_chat(system_prompt, prompt))
    if not content.strip():
        raise LLMError("AI 服务返回了空内容，请稍后重试")
    return content


def stream_health_assessment(prompt):
    return stream_chat(HEALTH_SYSTEM_PROMPT, prompt)


def stream_sport_prescription(prompt):
    return stream_chat(SPORT_SYSTEM_PROMPT, prompt)


def get_health_assessment(prompt):
    """生成健康评估报告"""
    return chat(HEALTH_SYSTEM_PROMPT, prompt)


def get_sport_prescription(prompt):
    """生成运动处方"""
    return chat(SPORT_SYSTEM_PROMPT, prompt)
