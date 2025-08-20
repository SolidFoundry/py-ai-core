# --- START OF FILE py_ai_core/core/logging_filters.py ---
import logging
from py_ai_core.core.context import request_id_var


class RequestIDFilter(logging.Filter):
    """
    这是一个日志过滤器，它将contextvar中的request_id注入到日志记录中。
    """

    def filter(self, record: logging.LogRecord) -> bool:
        # 从contextvar获取请求ID，如果不存在则使用'N/A'
        record.request_id = request_id_var.get("N/A")
        return True


# --- END OF FILE py_ai_core/core/logging_filters.py ---
