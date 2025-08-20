# --- START OF FILE tests/test_mcp_router.py ---

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock, patch

from py_ai_core.main import app

# 创建一个 TestClient 实例
client = TestClient(app)


# 使用 pytest.fixture 来创建一个可复用的 mocker 设置
# 这样每个测试函数都能在一个干净的 mock 环境下运行
@pytest.fixture(autouse=True)
def auto_mock_services(mocker):
    """
    这个 fixture 会在每个测试函数运行前自动执行，
    它会 mock 掉所有 router 依赖的外部服务。
    """
    # Mock 所有 session_service 的方法
    mocker.patch(
        "py_ai_core.mcp.router.session_service.get_or_create_session_prompt",
        new_callable=AsyncMock,
        return_value="默认系统提示词",
    )
    mocker.patch(
        "py_ai_core.mcp.router.session_service.get_history",
        new_callable=AsyncMock,
        return_value=[],
    )
    mocker.patch(
        "py_ai_core.mcp.router.session_service.update_history", new_callable=AsyncMock
    )

    # Mock 所有 llm_service 的方法
    mocker.patch(
        "py_ai_core.mcp.router.llm_service.get_model_decision", new_callable=AsyncMock
    )
    mocker.patch(
        "py_ai_core.mcp.router.llm_service.get_summary_from_tool_results",
        new_callable=AsyncMock,
    )

    # Mock execute_tool 辅助函数
    mocker.patch("py_ai_core.mcp.router.execute_tool", new_callable=AsyncMock)


def test_chat_endpoint_missing_session_id():
    """
    测试: 当请求中缺少 session_id 时，应返回 400 错误。
    """
    response = client.post("/v1/mcp/chat", json={"query": "你好"})
    assert response.status_code == 400
    assert response.json()["detail"] == "session_id is required."


def test_chat_endpoint_direct_answer():
    """
    测试: 当大模型直接回答时，聊天端点能否正确处理。
    """
    # === 准备 (Arrange) ===
    # 1. 准备假的 LLM 响应
    fake_model_message = MagicMock()
    fake_model_message.content = "你好，我是AI助手！"
    fake_model_message.tool_calls = None

    # 2. 获取并配置被 auto_mock_services 创建的 mocks
    with patch(
        "py_ai_core.mcp.router.llm_service.get_model_decision",
        new_callable=AsyncMock,
        return_value=fake_model_message,
    ) as mock_get_decision, patch(
        "py_ai_core.mcp.router.session_service.update_history", new_callable=AsyncMock
    ) as mock_update_history:

        # 3. 准备客户端请求数据
        request_data = {"query": "你好", "session_id": "test-session-direct"}

        # === 执行 (Act) ===
        response = client.post("/v1/mcp/chat", json=request_data)

        # === 断言 (Assert) ===
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["answer"] == "你好，我是AI助手！"
        assert response_json["session_id"] == "test-session-direct"

        # 验证正确的 mock 被调用
        mock_get_decision.assert_awaited_once()
        mock_update_history.assert_awaited_once()


def test_chat_endpoint_with_tool_call():
    """
    测试: 当大模型决定调用工具时，整个 ReAct 流程能否正确执行。
    """
    # === 准备 (Arrange) ===
    # 1. 准备所有假数据
    fake_tool_call = MagicMock()
    fake_tool_call.id = "call_123"
    fake_tool_call.function.name = "get_current_weather"
    fake_tool_call.function.arguments = '{"city": "北京"}'

    fake_model_decision_message = MagicMock()
    fake_model_decision_message.content = None
    fake_model_decision_message.tool_calls = [fake_tool_call]
    # 需要 mock model_dump 方法
    fake_model_decision_message.model_dump.return_value = {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": "call_123",
                "function": {
                    "name": "get_current_weather",
                    "arguments": '{"city": "北京"}',
                },
                "type": "function",
            }
        ],
    }

    fake_tool_result = {
        "role": "tool",
        "tool_call_id": "call_123",
        "name": "get_current_weather",
        "content": "北京的天气是晴朗, 25度 celsius.",
    }

    fake_final_summary = "根据工具查询，北京今天天气晴朗，气温是25摄氏度。"

    # 2. 配置由 fixture 创建的 mocks
    with patch(
        "py_ai_core.mcp.router.llm_service.get_model_decision",
        new_callable=AsyncMock,
        return_value=fake_model_decision_message,
    ) as mock_get_decision, patch(
        "py_ai_core.mcp.router.execute_tool",
        new_callable=AsyncMock,
        return_value=fake_tool_result,
    ) as mock_execute_tool, patch(
        "py_ai_core.mcp.router.llm_service.get_summary_from_tool_results",
        new_callable=AsyncMock,
        return_value=fake_final_summary,
    ) as mock_get_summary, patch(
        "py_ai_core.mcp.router.session_service.update_history", new_callable=AsyncMock
    ) as mock_update_history:

        # 3. 准备客户端请求
        request_data = {"query": "北京天气怎么样？", "session_id": "test-session-tool"}

        # === 执行 (Act) ===
        response = client.post("/v1/mcp/chat", json=request_data)

        # === 断言 (Assert) ===
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["answer"] == fake_final_summary
        assert response_json["session_id"] == "test-session-tool"

        # 验证所有关键函数都被正确调用
        mock_get_decision.assert_awaited_once()
        mock_execute_tool.assert_awaited_once()
        mock_get_summary.assert_awaited_once()
        mock_update_history.assert_awaited_once()

        # 验证 execute_tool 的调用参数
        mock_execute_tool.assert_awaited_with(fake_tool_call, "test-session-tool")


# --- END OF FILE tests/test_mcp_router.py ---
