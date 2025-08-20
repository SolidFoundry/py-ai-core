# 问题排查指南

本文档帮助你解决 py-ai-core 项目中的常见问题。

## 🐳 Docker 相关问题

### 1. 容器启动失败

**问题描述：** 容器无法启动或立即退出

**解决方案：**
```bash
# 查看容器日志
docker-compose logs app

# 重新构建镜像
docker-compose build --no-cache

# 清理并重新启动
docker-compose down -v
docker-compose up -d
```

### 2. 数据库连接失败

**问题描述：** 应用无法连接到数据库

**解决方案：**
```bash
# 检查数据库容器状态
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 重启数据库服务
docker-compose restart db
```

### 3. 依赖版本冲突

**问题描述：** Docker构建时出现依赖版本冲突错误

**解决方案：**
```bash
# 使用修复脚本（推荐）
scripts\fix-docker.bat          # Windows
./scripts/fix-docker.sh         # Linux/macOS

# 手动清理Docker缓存
docker system prune -a

# 重新构建镜像
docker-compose build --no-cache

# 如果仍有问题，检查Dockerfile中的版本兼容性
```

### 4. 使用简化Dockerfile

**问题描述：** 复杂的Dockerfile导致构建失败

**解决方案：**
```bash
# 项目现在提供两个Dockerfile：
# - Dockerfile: 完整版本（可能有依赖冲突）
# - Dockerfile.simple: 简化版本（推荐使用）

# 使用简化版本构建
docker-compose build --no-cache
```

## 🧪 测试相关问题

### 1. 测试失败

**问题描述：** 运行测试时出现错误

**解决方案：**
```bash
# 在容器中运行测试
scripts\dev.bat test          # Windows
./scripts/dev.sh test         # Linux/macOS

# 查看详细错误信息
docker-compose --profile test run --rm test test -v
```

### 2. 测试依赖缺失

**问题描述：** 测试时提示模块找不到

**解决方案：**
```bash
# 重新构建镜像（包含测试依赖）
docker-compose build --no-cache

# 检查容器中是否安装了pytest
docker-compose --profile test run --rm test which pytest
```

### 3. pytest命令未找到

**问题描述：** 容器中找不到pytest命令

**解决方案：**
```bash
# 检查容器中的Python路径
docker-compose --profile test run --rm test python -c "import sys; print(sys.path)"

# 重新构建镜像
docker-compose build --no-cache

# 使用Python模块方式运行
docker-compose --profile test run --rm test python -m pytest
```

## 🔧 开发环境问题

### 1. 代码热重载不工作

**问题描述：** 修改代码后应用没有自动重启

**解决方案：**
```bash
# 确保使用开发环境配置
scripts\dev.bat dev           # Windows
./scripts/dev.sh dev          # Linux/macOS

# 重启开发服务
docker-compose restart app
```

### 2. 脚本窗口自动退出

**问题描述：** Windows批处理脚本执行后立即退出

**解决方案：**
```bash
# 在脚本末尾添加pause命令
# 确保脚本有正确的错误处理
# 检查脚本中的exit命令
```

### 3. 环境配置文件问题

**问题描述：** 找不到.env.example文件

**解决方案：**
```bash
# 项目现在使用env.example文件
# 复制配置文件
copy env.example .env          # Windows
cp env.example .env           # Linux/macOS

# 编辑.env文件，填入API密钥
```

## 🌐 网络相关问题

### 1. API 无法访问

**问题描述：** 无法访问 http://localhost:8000

**解决方案：**
```bash
# 检查应用状态
docker-compose ps app

# 查看应用日志
docker-compose logs app

# 检查端口是否被占用
netstat -an | findstr :8000    # Windows
netstat -an | grep :8000       # Linux/macOS
```

## 🔑 配置相关问题

### 1. 环境变量未生效

**问题描述：** 修改 .env 文件后配置没有更新

**解决方案：**
```bash
# 重启服务
docker-compose restart

# 检查环境变量
docker-compose exec app env | grep OPENAI

# 确保.env文件格式正确（无空格，无引号）
```

### 2. OpenAI API密钥问题

**问题描述：** API调用失败，提示密钥无效

**解决方案：**
```bash
# 检查.env文件中的API密钥
# 确保密钥格式正确：sk-xxxxxxxxxxxxxxxxxxxxxxxx
# 验证密钥是否有效
# 检查账户余额和API限制
```

## 📞 获取帮助

如果以上解决方案无法解决你的问题：

1. **查看日志：** 使用 `docker-compose logs` 查看详细错误信息
2. **搜索 Issues：** 在 GitHub Issues 中搜索类似问题
3. **创建 Issue：** 提供详细的错误信息和环境描述

## 🔍 调试技巧

### 1. 进入容器调试

```bash
# 进入应用容器
docker-compose exec app bash

# 进入测试容器
docker-compose --profile test run --rm test bash

# 进入开发容器
docker-compose --profile dev run --rm dev bash
```

### 2. 查看实时日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f app
```

### 3. 检查容器状态

```bash
# 查看所有容器状态
docker-compose ps

# 查看容器详细信息
docker-compose ps -a

# 查看容器资源使用
docker stats
```

## 🚀 快速修复命令

### Windows用户
```cmd
# 使用修复脚本（推荐）
scripts\fix-docker.bat

# 手动修复
scripts\dev.bat clean
scripts\dev.bat build
scripts\dev.bat run
scripts\dev.bat test
```

### Linux/macOS用户
```bash
# 使用修复脚本（推荐）
./scripts/fix-docker.sh

# 手动修复
./scripts/dev.sh clean
./scripts/dev.sh build
./scripts/dev.sh run
./scripts/dev.sh test
```

## 🔧 一键修复方案

### 方案1：使用修复脚本（推荐）
```bash
# Windows
scripts\fix-docker.bat

# Linux/macOS
./scripts/fix-docker.sh
```

### 方案2：手动清理重建
```bash
# 1. 清理环境
docker-compose down -v
docker system prune -a -f

# 2. 重新构建
docker-compose build --no-cache

# 3. 启动服务
docker-compose up -d
```

---

**提示：** 在提交 Issue 时，请包含完整的错误信息、环境描述和重现步骤。

**常见错误解决顺序：**
1. 使用修复脚本：`scripts\fix-docker.bat` 或 `./scripts/fix-docker.sh`
2. 如果仍有问题，手动清理：`docker-compose down -v && docker system prune -f`
3. 重新构建：`docker-compose build --no-cache`
4. 启动服务：`docker-compose up -d`
5. 查看日志：`docker-compose logs -f`
6. 如果仍有问题，检查配置文件和环境变量
