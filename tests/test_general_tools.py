# tests/test_general_tools.py

import pytest
from datetime import datetime

# 1. 从你的应用代码中，导入你需要测试的函数
from py_ai_core.tools.general_tools import get_current_datetime, get_current_weather

# 2. 告诉 pytest，这个文件里的测试用例需要异步执行
#    因为我们的工具函数都是 `async def`
pytestmark = pytest.mark.asyncio


# 3. 编写第一个测试函数，函数名必须以 `test_` 开头
async def test_get_current_datetime_format():
    """
    测试: get_current_datetime 函数返回的日期时间字符串格式是否正确。
    """
    # === 执行 (Act) ===
    # 调用我们要测试的函数，并用 await 等待结果
    result = await get_current_datetime()

    # === 断言 (Assert) ===
    # 这是测试的核心！`assert` 关键字用来判断一个条件是否为真。
    # 如果条件为假，测试就会失败。
    try:
        # 我们尝试用指定的格式去解析这个结果字符串。
        # 如果格式不匹配，`strptime` 会抛出一个 ValueError 异常。
        datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        # 如果代码能顺利执行到这里，说明格式正确，测试通过。
        assert True
    except ValueError:
        # 如果捕获到了 ValueError，说明格式不正确，我们主动让测试失败。
        assert False, f"日期格式不正确，期望 'YYYY-MM-DD HH:MM:SS'，但收到了 '{result}'"


async def test_get_current_weather_with_default_unit():
    """
    测试: get_current_weather 函数在给定城市时，能否返回预期的天气字符串。
    """
    # === 准备 (Arrange) ===
    city = "北京"
    expected_output = "北京的天气是晴朗, 30度 celsius."

    # === 执行 (Act) ===
    result = await get_current_weather(city=city)

    # === 断言 (Assert) ===
    # 我们断言函数的返回值是否和我们期望的完全一样。
    assert result == expected_output
