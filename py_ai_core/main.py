# --- START OF FILE py_ai_core/main.py (Final, Cleaned, with Tracing) ---

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

# ===================================================================
# 1. 在任何其他应用代码之前，立即配置日志系统
# ===================================================================
from py_ai_core.logging_config import setup_logging

setup_logging()

# ===================================================================
# 2. 导入所有需要的模块
# ===================================================================
from py_ai_core.core.database import engine, Base
from py_ai_core.models import db_models
from py_ai_core.mcp.router import router as mcp_router
from py_ai_core.mcp.ops_router import router as ops_router
from py_ai_core.core.middleware import CtxTimingMiddleware
from py_ai_core.core.utils import limiter
from py_ai_core.core.telemetry import setup_telemetry  # ✅ 导入OTel初始化函数
from py_ai_core import tools

# ✅ 清理: 删除了与 prometheus_fastapi_instrumentator 相关的所有导入
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# 获取一个已经配置好的logger实例
logger = logging.getLogger(__name__)


# ===================================================================
# 3. 后台任务与应用生命周期管理
# ===================================================================
async def heartbeat_task():
    """一个后台任务，每小时打印一次心跳日志。"""
    heartbeat_logger = logging.getLogger("py_ai_core.heartbeat")
    while True:
        heartbeat_logger.info("心跳: 服务正在运行...")
        await asyncio.sleep(3600)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI应用的生命周期管理器。"""
    # === 应用启动时执行 ===
    logger.info("应用启动流程开始...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("数据库表已检查并成功创建（如果不存在）。")
    except Exception as e:
        logger.exception("数据库表创建失败！错误: %s", e)
        raise

    # ✅ 在应用启动时，初始化遥测(Tracing)系统
    setup_telemetry(app)

    heartbeat = asyncio.create_task(heartbeat_task())
    logger.info("心跳日志后台任务已启动。")

    yield  # FastAPI应用在此处运行

    # === 应用关闭时执行 ===
    logger.info("应用正在关闭...")
    heartbeat.cancel()
    try:
        await heartbeat
    except asyncio.CancelledError:
        logger.info("心跳日志后台任务已成功取消。")
    logger.info("应用已成功关闭。")


# ===================================================================
# 4. 应用工厂函数
# ===================================================================
def create_app() -> FastAPI:
    """创建并配置FastAPI应用实例。"""
    app = FastAPI(
        title="Python AI 核心平台",
        description="一个可扩展、集成了多种AI能力的统一平台。",
        version="1.0.0",
        lifespan=lifespan,
    )

    # ✅ 清理: 删除了 Instrumentator()... 的调用

    # 将limiter实例的状态与app关联
    app.state.limiter = limiter

    # 添加 slowapi 的自定义异常处理器
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"detail": f"Rate limit exceeded: {exc.detail}"},
        )

    # 添加中间件 (顺序很重要，外层先添加)
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(CtxTimingMiddleware)
    logger.info("已成功加载所有中间件。")

    # 挂载路由
    app.include_router(ops_router)
    app.include_router(mcp_router, prefix="/v1/mcp", tags=["模型上下文协议 (MCP)"])
    logger.info("已成功挂载所有路由。")

    @app.get("/", tags=["根路径"])
    async def read_root():
        return {"message": "欢迎访问 Python AI 核心平台，请访问 /docs 查看 API 文档。"}

    logger.info("应用配置完成。")
    return app


# ===================================================================
# 5. 创建并导出应用实例
# ===================================================================
app = create_app()

# --- END OF FILE py_ai_core/main.py (Final, Cleaned, with Tracing) ---
