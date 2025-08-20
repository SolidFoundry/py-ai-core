# --- START OF FILE tests/test_session_service.py (Corrected Version) ---

import pytest
import json
from unittest.mock import MagicMock, AsyncMock

# 导入我们要测试的类和它依赖的模型
from py_ai_core.services.session_service import SessionService
from py_ai_core.models.db_models import ChatMessage, ChatSession
from py_ai_core.core.config import settings

# 标记所有测试为异步
pytestmark = pytest.mark.asyncio


@pytest.fixture
def service():
    """提供一个干净的 SessionService 实例"""
    return SessionService()


def create_mock_db_session():
    """创建一个配置更精确的模拟数据库会话的辅助函数"""
    mock_db = AsyncMock()
    # SQLAlchemy 的 session.add() 和 session.add_all() 是同步方法
    mock_db.add = MagicMock()
    mock_db.add_all = MagicMock()
    return mock_db


async def test_get_history_with_smart_truncation(service: SessionService):
    """
    测试: 智能滑动窗口能否在切断工具链时正确地回溯和补充历史。
    """
    # === 准备 (Arrange) ===
    fake_db_result_desc = [
        MagicMock(
            spec=ChatMessage,
            id=5,
            content=json.dumps({"role": "assistant", "content": "总结"}),
        ),
        MagicMock(
            spec=ChatMessage,
            id=4,
            content=json.dumps({"role": "tool", "name": "t", "content": "res"}),
        ),
        MagicMock(
            spec=ChatMessage,
            id=3,
            content=json.dumps({"role": "assistant", "tool_calls": []}),
        ),
        MagicMock(
            spec=ChatMessage,
            id=2,
            content=json.dumps({"role": "user", "content": "问题"}),
        ),
        MagicMock(
            spec=ChatMessage,
            id=1,
            content=json.dumps({"role": "assistant", "content": "你好"}),
        ),
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = fake_db_result_desc
    mock_db_session = create_mock_db_session()  # <-- 使用新的辅助函数
    mock_db_session.execute.return_value = mock_result

    # 假设窗口大小为3
    original_max_history = settings.MAX_HISTORY_MESSAGES
    settings.MAX_HISTORY_MESSAGES = 3

    # === 执行 (Act) ===
    history = await service.get_history("test-session", mock_db_session)

    # === 断言 (Assert) ===
    assert len(history) == 4
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "问题"

    # 恢复原始设置
    settings.MAX_HISTORY_MESSAGES = original_max_history


async def test_get_or_create_session_prompt_creates_new_session(
    service: SessionService,
):
    """
    测试: 当 session 不存在时，能否创建新 session 并返回默认 prompt。
    """
    # 准备:
    mock_session_result = MagicMock()
    mock_session_result.scalars.return_value.first.return_value = None
    mock_db = create_mock_db_session()  # <-- 使用新的辅助函数
    mock_db.execute.return_value = mock_session_result

    # 执行
    prompt = await service.get_or_create_session_prompt("new-session", mock_db)

    # 断言
    assert prompt == settings.DEFAULT_SYSTEM_PROMPT
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()


async def test_get_or_create_session_prompt_updates_existing(service: SessionService):
    """
    测试: 当提供了新的 prompt 时，能否更新现有 session。
    """
    # 准备:
    existing_session = ChatSession(
        session_id="existing-session", system_prompt="旧的提示词"
    )
    mock_session_result = MagicMock()
    mock_session_result.scalars.return_value.first.return_value = existing_session
    mock_db = create_mock_db_session()  # <-- 使用新的辅助函数
    mock_db.execute.return_value = mock_session_result

    new_prompt = "这是新的海盗提示词！"

    # 执行
    prompt = await service.get_or_create_session_prompt(
        "existing-session", mock_db, requested_prompt=new_prompt
    )

    # 断言
    assert prompt == new_prompt
    assert existing_session.system_prompt == new_prompt
    mock_db.commit.assert_awaited_once()


async def test_update_history(service: SessionService):
    """
    测试: update_history 方法能否正确地添加新消息并提交到数据库。
    """
    mock_db_session = create_mock_db_session()  # <-- 使用新的辅助函数

    session_id = "test-session-update"
    new_messages = [
        {"role": "user", "content": "新问题"},
        {"role": "assistant", "content": "新回答"},
    ]

    await service.update_history(
        session_id=session_id, new_messages=new_messages, db=mock_db_session
    )

    mock_db_session.add_all.assert_called_once()
    mock_db_session.commit.assert_awaited_once()

    added_objects = mock_db_session.add_all.call_args[0][0]

    assert isinstance(added_objects, list)
    assert len(added_objects) == 2
    first_message = added_objects[0]
    assert isinstance(first_message, ChatMessage)
    assert first_message.session_id == session_id
    assert first_message.role == "user"
    assert json.loads(first_message.content)["content"] == "新问题"


# --- END OF FILE tests/test_session_service.py (Corrected Version) ---
