# --- START OF FILE py_ai_core/models/schemas.py ---

from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    # ✅ 允许客户端在请求中指定或更新 system_prompt
    system_prompt: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    session_id: Optional[str] = None


# --- END OF FILE py_ai_core/models/schemas.py ---
