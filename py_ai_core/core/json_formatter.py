# --- START OF FILE py_ai_core/core/json_formatter.py (Correct, Final, Standard Version) ---

from datetime import datetime
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    一个自定义的JSON格式化器，实现了完美的字段排序和标准的时间格式。
    """

    def add_fields(self, log_record, record, message_dict):
        # 调用父类方法获取所有基础字段
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        # 创建一个新的有序字典，以我们期望的顺序重建日志
        ordered_log_record = {}

        # 1. 黄金顺序：时间 -> 内容 -> 关联ID
        now = datetime.fromtimestamp(record.created)
        ordered_log_record["timestamp"] = (
            now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        )
        ordered_log_record["message"] = log_record.get("message", "")
        ordered_log_record["request_id"] = log_record.get("request_id", "N/A")

        # 2. 将剩余的所有其他字段追加到后面
        for key, value in log_record.items():
            if key not in ordered_log_record:
                ordered_log_record[key] = value

        # 3. 用排序完美的字典替换原始字典
        log_record.clear()
        log_record.update(ordered_log_record)


# --- END OF FILE py_ai_core/core/json_formatter.py (Correct, Final, Standard Version) ---
