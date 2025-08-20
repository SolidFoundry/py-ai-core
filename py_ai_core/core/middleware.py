# --- START OF FILE py_ai_core/core/middleware.py (Final Simplified Version) ---

import time
import uuid
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from py_ai_core.core.context import request_id_var

access_logger = logging.getLogger("py_ai_core.access")


class CtxTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = str(uuid.uuid4())
        token = request_id_var.set(request_id)

        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        process_time_ms = int(process_time * 1000)

        response.headers["X-Process-Time-Ms"] = str(process_time_ms)
        response.headers["X-Request-ID"] = request_id

        log_message = "request handled"

        # ✅✅✅ 关键修正: 直接将要添加的字段构造成一个字典 ✅✅✅
        extra_data = {
            "http": {
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "client": {
                    "host": request.client.host,
                    "port": request.client.port,
                },
                "status_code": response.status_code,
            },
            "duration": {"ms": process_time_ms},
        }

        # 使用 extra 参数传递这个字典，python-json-logger会自动处理
        access_logger.info(log_message, extra=extra_data)

        request_id_var.reset(token)

        return response


# --- END OF FILE py_ai_core/core/middleware.py (Final Simplified Version) ---
