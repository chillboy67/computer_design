"""用本地模拟的 OpenAI 兼容服务测试大模型调用（不访问真实服务）"""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

import config
import llm_utils
from llm_utils import LLMError, chat, stream_chat


class FakeService(BaseHTTPRequestHandler):
    requests = []
    status = 200

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        FakeService.requests.append({"path": self.path, "auth": self.headers.get("Authorization"), "body": body})
        if FakeService.status != 200:
            self.send_response(FakeService.status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": {"message": "invalid api key"}}')
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        for piece in ["## 运动", "项目\n快走"]:
            chunk = {"id": "1", "object": "chat.completion.chunk", "created": 1, "model": body["model"],
                     "choices": [{"index": 0, "delta": {"content": piece}, "finish_reason": None}]}
            self.wfile.write(f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n".encode())
        self.wfile.write(b"data: [DONE]\n\n")

    def log_message(self, *args):
        pass


@pytest.fixture
def service(monkeypatch):
    server = HTTPServer(("127.0.0.1", 0), FakeService)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    FakeService.requests = []
    FakeService.status = 200
    monkeypatch.setattr(config, "LLM_API_KEY", "sk-other-provider")
    monkeypatch.setattr(config, "LLM_BASE_URL", f"http://127.0.0.1:{server.server_port}/v1")
    monkeypatch.setattr(config, "LLM_MODEL", "deepseek-chat")
    llm_utils._get_client.cache_clear()
    yield FakeService
    server.shutdown()
    llm_utils._get_client.cache_clear()


def test_openai_compatible_service(service):
    assert "".join(stream_chat("系统提示", "用户输入")) == "## 运动项目\n快走"
    request = service.requests[0]
    assert request["path"] == "/v1/chat/completions"
    assert request["auth"] == "Bearer sk-other-provider"
    body = request["body"]
    assert body["model"] == "deepseek-chat" and body["stream"] is True
    assert body["messages"][0] == {"role": "system", "content": "系统提示"}
    assert None not in body.values()  # 不发送值为 null 的参数


def test_service_error_is_reported(service):
    service.status = 401
    with pytest.raises(LLMError, match="AI 服务调用失败"):
        chat("系统提示", "用户输入")


def test_missing_api_key(monkeypatch):
    monkeypatch.setattr(config, "LLM_API_KEY", "")
    llm_utils._get_client.cache_clear()
    with pytest.raises(LLMError, match="LLM_API_KEY"):
        chat("系统提示", "用户输入")
    llm_utils._get_client.cache_clear()
