# --- START OF FILE tests/conftest.py (Final Intelligent Version) ---

import builtins
import os

# 1. 打印清晰的日志
print("\n" + "="*60)
print("Applying INTELLIGENT monkey patch from tests/conftest.py...")
print("="*60 + "\n")

# 2. 保存原始的 open 函数
original_open = builtins.open

def intelligent_utf8_open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
    """
    一个更智能的open函数补丁。
    它只在文本模式(mode不含'b')且未指定编码时，才强制使用'utf-8'。
    对于二进制模式(mode含'b')，它完全不干预encoding参数。
    """
    # ✅✅✅ 关键修正：增加判断逻辑 ✅✅✅
    if 'b' not in mode:  # 如果不是二进制模式
        if encoding is None: # 并且没有指定编码
            encoding = 'utf-8' # 我们才介入

    # 调用原始的open函数，并传递可能被我们修正过的encoding
    return original_open(
        file,
        mode=mode,
        buffering=buffering,
        encoding=encoding,
        errors=errors,
        newline=newline,
        closefd=closefd,
        opener=opener
    )

# 3. 应用我们更智能的补丁
builtins.open = intelligent_utf8_open

# 4. 环境变量作为双保险
os.environ['PYTHONUTF8'] = '1'

# --- END OF FILE tests/conftest.py (Final Intelligent Version) ---