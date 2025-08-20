# --- START OF FILE py_ai_core/core/config.py (Final Encoding-Safe Version) ---

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- LLM 配置 ---
    OPENAI_API_KEY: str
    OPENAI_API_BASE: str
    MODEL_NAME: str

    # --- 数据库配置 ---
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str

    # --- 会话管理 ---
    MAX_HISTORY_MESSAGES: int = 10
    
    # --- 日志系统的高级配置 ---
    LOG_PAYLOADS: bool = False 

    # --- 默认的系统提示词 ---
    DEFAULT_SYSTEM_PROMPT: str = (
        "你是一个通用的万能助手，名叫万能。"
        "请友好、专业地回答用户问题。"
        "特别注意：当且仅当遇到任何需要数学计算或处理数值的问题时，"
        "你必须使用且只能使用 'calculate' 工具来获得精确结果，"
        "不要依赖自己的知识进行计算。"
    )

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """
        生成异步 SQLAlchemy 数据库连接字符串。
        """
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    # model_config 是 Pydantic v2 中用于配置模型行为的地方
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8" # 告诉 Pydantic (以及依赖它的Starlette) 用UTF-8读取.env
    )

settings = Settings()

# --- END OF FILE py_ai_core/core/config.py (Final Encoding-Safe Version) ---