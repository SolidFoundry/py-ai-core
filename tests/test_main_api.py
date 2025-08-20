# --- START OF FILE tests/test_main_api.py ---

from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from py_ai_core.main import app

client = TestClient(app)


def test_read_root():
    """
    集成测试: 测试根路径 GET / 是否能成功返回欢迎信息。
    """
    response = client.get("/")
    assert response.status_code == 200
    # ✅ 修正: 欢迎语可能已更新，与 README 或代码保持一致
    assert "欢迎访问 Python AI 核心平台" in response.json()["message"]


def test_chat_endpoint_requires_session_id():
    """
    单元测试: 验证在不提供 session_id 的情况下，/chat 接口返回 400 错误。
    """
    request_body = {"query": "你好"}
    response = client.post("/v1/mcp/chat", json=request_body)

    # ✅ 修正: 根据代码逻辑，缺少 session_id 应该返回 400，而不是 200。
    assert response.status_code == 400
    assert response.json() == {"detail": "session_id is required."}


# 为了让这个文件里的测试通过，我们也需要 mock 掉 chat 接口的依赖
# 否则，即使提供了 session_id，它也会尝试真的调用 LLM API
@patch(
    "py_ai_core.mcp.router.session_service.get_or_create_session_prompt",
    new_callable=AsyncMock,
)
@patch(
    "py_ai_core.mcp.router.session_service.get_history",
    new_callable=AsyncMock,
    return_value=[],
)
@patch("py_ai_core.mcp.router.llm_service.get_model_decision", new_callable=AsyncMock)
@patch("py_ai_core.mcp.router.session_service.update_history", new_callable=AsyncMock)
def test_chat_endpoint_with_session_id_smoketest(
    mock_update, mock_decision, mock_history, mock_prompt
):
    """
    冒烟测试: 在提供了 session_id 和所有依赖都被 mock 的情况下，接口能返回 200。
    """
    # 配置 mock 返回值
    mock_prompt.return_value = "默认提示词"
    fake_model_message = AsyncMock()
    fake_model_message.content = "模拟回复"
    fake_model_message.tool_calls = None
    mock_decision.return_value = fake_model_message

    request_body = {"query": "你好", "session_id": "smoke-test-session"}
    response = client.post("/v1/mcp/chat", json=request_body)

    assert response.status_code == 200
    assert "answer" in response.json()
    assert response.json()["answer"] == "模拟回复"


# --- END OF FILE tests/test_main_api.py ---
