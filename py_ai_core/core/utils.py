# --- py_ai_core/core/utils.py ---
from slowapi import Limiter
from slowapi.util import get_remote_address
from cachetools import TTLCache

limiter = Limiter(key_func=get_remote_address)
health_check_cache = TTLCache(maxsize=1, ttl=5)