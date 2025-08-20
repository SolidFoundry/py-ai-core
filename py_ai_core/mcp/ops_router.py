# --- START OF FILE py_ai_core/mcp/ops_router.py (Final Dependency Injection Version) ---
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel

from py_ai_core.core.database import get_db
from py_ai_core.core.utils import limiter, health_check_cache

logger = logging.getLogger(__name__)
router = APIRouter()

class HealthCheckResponse(BaseModel):
    status: str
    database_connection: str

# ✅ 1. 创建一个专门用于速率限制的依赖项
#    我们将速率限制的逻辑封装在这个函数里。
#    FastAPI会在调用 health_check 之前，先执行这个函数。
@limiter.limit("60/minute")
async def rate_limit_dependency(request: Request):
    """
    这是一个依赖项，它本身不返回任何东西，
    它的唯一作用就是被slowapi的装饰器包装，
    以便在速率超限时抛出 RateLimitExceeded 异常。
    """
    return

HEALTH_CHECK_CACHE_KEY = "health_check_result"

@router.get(
    "/health",
    tags=["运维(Operations)"],
    summary="执行服务健康检查",
    response_model=HealthCheckResponse,
    # API文档保持不变
    responses={
        429: {"description": "请求过于频繁 (Rate Limit Exceeded)"},
        503: {"description": "服务不可用 (例如，数据库连接失败)"},
    },
    # ✅ 2. 在这里通过 Depends() 使用我们的速率限制依赖项
    dependencies=[Depends(rate_limit_dependency)],
)
async def health_check(request: Request, db: AsyncSession = Depends(get_db)):
    """
    一个受速率限制和缓存保护的综合健康检查端点。
    - Rate Limit: 60 requests per minute per IP.
    - Cache: Results are cached for 5 seconds.
    """
    # 手动缓存逻辑保持不变，它已经被证明是异步安全的
    try:
        cached_response = health_check_cache[HEALTH_CHECK_CACHE_KEY]
        logger.debug("健康检查命中缓存。")
        return cached_response
    except KeyError:
        logger.debug("健康检查未命中缓存，执行实际的数据库查询...")
        db_status = "ok"
        try:
            result = await db.execute(text("SELECT 1"))
            if result.scalar_one() != 1:
                raise Exception("Database returned unexpected result.")
        except Exception as e:
            logger.error("健康检查失败：数据库连接异常！错误: %s", e, exc_info=True)
            db_status = "error"
            raise HTTPException(
                status_code=503,
                detail={"status": "error", "database_connection": f"failed: {e}"},
            )

        response = HealthCheckResponse(status="ok", database_connection=db_status)
        health_check_cache[HEALTH_CHECK_CACHE_KEY] = response
        return response

# --- END OF FILE py_ai_core/mcp/ops_router.py (Final Dependency Injection Version) ---