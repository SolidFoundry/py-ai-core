# --- START OF FILE py_ai_core/mcp/router.py ---

import json
import asyncio
import logging
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from openai.types.chat import ChatCompletionMessage

from py_ai_core.core.database import get_db
from py_ai_core.models.schemas import ChatRequest, ChatResponse
from py_ai_core.services.llm_service import llm_service
from py_ai_core.services.session_service import session_service
from py_ai_core.tools.registry import tool_registry

# ✅ 关键修复: 导入 tools 包，这将触发 __init__.py 中的工具自动注册。
# 这一行导入是为了执行工具注册的“副作用”，即使这里没有直接使用 `tools` 变量。
from py_ai_core import tools


logger = logging.getLogger(__name__)

router = APIRouter()

# --- 主路由函数 ---


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """处理聊天请求的核心端点。现在逻辑更清晰，负责主流程编排。"""
    session_id = request.session_id
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")

    logger.info("收到新的聊天请求，会话ID: '%s'", session_id)
    logger.debug("会话 '%s' 的原始请求体: %s", session_id, request.model_dump_json())

    try:
        # 1. 准备请求上下文
        system_prompt_content = await session_service.get_or_create_session_prompt(
            session_id, db, request.system_prompt
        )
        history_messages = await session_service.get_history(session_id, db)

        system_message = {"role": "system", "content": system_prompt_content}
        current_user_message = {"role": "user", "content": request.query}
        messages_for_llm = [system_message] + history_messages + [current_user_message]

        # 2. 从LLM获取决策
        tool_schemas = tool_registry.get_all_schemas()
        model_message = await llm_service.get_model_decision(
            messages_for_llm, tool_schemas
        )
        if not model_message:
            raise HTTPException(status_code=500, detail="与大模型通信失败。")

        # 3. 根据决策分发任务
        if model_message.tool_calls:
            final_answer, messages_to_save = await _handle_tool_calls(
                session_id=session_id,
                model_message=model_message,
                messages_for_llm=messages_for_llm,
                current_user_message=current_user_message,
            )
        else:
            final_answer, messages_to_save = _handle_direct_answer(
                model_message=model_message,
                current_user_message=current_user_message,
            )

        # 4. 保存交互历史
        await session_service.update_history(session_id, messages_to_save, db)

        # 5. 返回最终结果
        return ChatResponse(answer=final_answer, session_id=session_id)

    except Exception as e:
        logger.exception("处理会话 '%s' 的请求时发生未知错误。", session_id)
        raise HTTPException(status_code=500, detail="处理请求时发生内部错误。")


# --- 内部辅助函数 (所有辅助函数保持不变) ---


async def _handle_tool_calls(
    session_id: str,
    model_message: ChatCompletionMessage,
    messages_for_llm: List[Dict[str, Any]],
    current_user_message: Dict[str, Any],
) -> tuple[str, List[Dict[str, Any]]]:
    """处理模型决定调用工具的逻辑分支。"""
    logger.info(
        "大模型决定为会话 '%s' 调用工具: %s",
        session_id,
        [tc.function.name for tc in model_message.tool_calls],
    )
    assistant_message_with_tool_calls = model_message.model_dump(exclude_unset=True)
    tasks = [execute_tool(tc, session_id) for tc in model_message.tool_calls]
    tool_results = await asyncio.gather(*tasks)
    messages_for_summary = (
        messages_for_llm + [assistant_message_with_tool_calls] + tool_results
    )
    final_answer = await llm_service.get_summary_from_tool_results(messages_for_summary)
    messages_to_save = [
        current_user_message,
        assistant_message_with_tool_calls,
        *tool_results,
        {"role": "assistant", "content": final_answer},
    ]
    return final_answer, messages_to_save


def _handle_direct_answer(
    model_message: ChatCompletionMessage,
    current_user_message: Dict[str, Any],
) -> tuple[str, List[Dict[str, Any]]]:
    """处理模型直接回答的逻辑分支。"""
    logger.info("大模型提供了直接回答。")
    final_answer = model_message.content or "抱歉，我无法回答。"
    messages_to_save = [
        current_user_message,
        {"role": "assistant", "content": final_answer},
    ]
    return final_answer, messages_to_save


async def execute_tool(tool_call, session_id: str):
    """安全地执行单个工具。"""
    tool_name = tool_call.function.name
    logger.info("正在为会话 '%s' 执行工具: '%s'", session_id, tool_name)
    tool_to_call = tool_registry.get_tool(tool_name)
    if not tool_to_call:
        error_msg = f"错误: 找不到名为 '{tool_name}' 的工具。"
        logger.error(
            "为会话 '%s' 尝试调用一个不存在的工具: '%s'", session_id, tool_name
        )
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_name,
            "content": error_msg,
        }
    try:
        tool_args_str = tool_call.function.arguments
        tool_args = json.loads(tool_args_str)
        logger.debug(
            "为会话 '%s' 调用工具 '%s' 的参数: %s", session_id, tool_name, tool_args
        )
        result = await tool_to_call(**tool_args)
        str_result = str(result)
        logger.info("为会话 '%s' 成功执行工具 '%s'。", session_id, tool_name)
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_name,
            "content": str_result,
        }
    except Exception as e:
        logger.exception("为会话 '%s' 执行工具 '%s' 时失败。", session_id, tool_name)
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_name,
            "content": f"执行失败: {e}",
        }


# --- END OF FILE py_ai_core/mcp/router.py ---
