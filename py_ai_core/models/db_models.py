# --- START OF FILE py_ai_core/models/db_models.py ---

import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from py_ai_core.core.database import Base


class ChatSession(Base):
    """
    ChatSession 数据模型，对应 'chat_sessions' 表。
    用于存储每个会话的元数据，比如它的角色设定 (system_prompt)。
    """

    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)

    # session_id 现在是这张表的主角，并且必须唯一
    session_id = Column(String(255), unique=True, index=True, nullable=False)

    # 存储这个会话绑定的 system_prompt
    system_prompt = Column(Text, nullable=True)  # 允许为空，表示使用默认prompt

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<ChatSession(id={self.id}, session_id='{self.session_id}')>"


class ChatMessage(Base):
    """
    ChatMessage 数据模型，对应数据库中的 'chat_messages' 表。
    """

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, session_id='{self.session_id}', role='{self.role}')>"


# --- END OF FILE py_ai_core/models/db_models.py ---
