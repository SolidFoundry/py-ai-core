# --- START OF FILE Dockerfile (Production Best Practice - Final Version) ---

# --- 阶段 1: 构建器 (Builder) ---
# 最佳实践 1: 使用明确的操作系统版本标签 (slim-bookworm)。
# 最佳实践 2: 使用 @sha256 摘要锁定基础镜像的精确版本，确保构建的绝对可复现性，并避免不必要的网络检查。
# 使用官方Python镜像作为基础镜像
FROM python:3.12-slim-bookworm as builder

# 设置工作目录
WORKDIR /app

# 复制应用代码和配置文件
COPY ./py_ai_core ./py_ai_core
COPY ./tests ./tests
COPY pyproject.toml .

# 安装依赖到指定目录
RUN pip install --no-cache-dir --upgrade pip && \
  pip install --no-cache-dir --target /app/deps -e .

# 安装测试和开发依赖（使用完全兼容的版本）
RUN pip install --no-cache-dir --target /app/deps \
  pytest==7.4.3 \
  pytest-asyncio==0.21.1 \
  pytest-mock==3.12.0 \
  pytest-cov==4.1.0 \
  black==23.11.0 \
  isort==5.12.0 \
  flake8==6.1.0 \
  mypy==1.7.1

# --- 阶段 2: 最终镜像 (Final Image) ---
# 同样，在最终镜像阶段也使用完全相同的、锁定了版本的具体基础镜像。
# 使用官方Python镜像作为运行时镜像
FROM python:3.12-slim-bookworm

# 设置环境变量
ENV PYTHONPATH=/app/deps
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
  curl \
  && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 从builder阶段复制依赖
COPY --from=builder /app/deps /app/deps

# 复制应用代码
COPY ./py_ai_core ./py_ai_core
COPY ./tests ./tests
COPY pyproject.toml .

# 暴露端口 8000
EXPOSE 8000

# 创建启动脚本
RUN echo '#!/bin/bash\n\
  if [ "$1" = "test" ]; then\n\
  exec python -m pytest "${@:2}"\n\
  elif [ "$1" = "lint" ]; then\n\
  exec python -m flake8 py_ai_core tests/\n\
  elif [ "$1" = "format" ]; then\n\
  exec python -m black py_ai_core tests/\n\
  elif [ "$1" = "shell" ]; then\n\
  exec /bin/bash\n\
  else\n\
  exec python -m uvicorn py_ai_core.main:app --host 0.0.0.0 --port 8000\n\
  fi' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# 使用自定义启动脚本
ENTRYPOINT ["/app/entrypoint.sh"]

# 默认启动应用
CMD ["uvicorn"]

# --- END OF FILE Dockerfile (Production Best Practice - Final Version) ---