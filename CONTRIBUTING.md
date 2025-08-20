# 贡献指南

感谢你考虑为 py-ai-core 项目做出贡献！这个文档将指导你如何参与项目开发。

## 🚀 快速开始

### 1. Fork 和克隆项目

1. 在 GitHub 上 Fork 这个项目
2. 克隆你的 Fork 到本地：
   ```bash
   git clone https://github.com/SolidFoundry/py-ai-core.git
   cd py-ai-core
   ```

### 2. 设置开发环境

#### 使用 Docker（推荐）

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑 .env 文件，填入你的配置
# 启动开发环境
docker-compose up -d

# 运行测试
docker-compose run --rm app pytest
```

#### 使用本地 Python 环境

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 安装依赖
pip install -e .

# 安装开发依赖
pip install pytest pytest-asyncio pytest-mock black isort

# 启动数据库（需要 Docker）
docker-compose up -d db

# 运行测试
pytest
```

## 📝 开发流程

### 1. 创建功能分支

```bash
# 确保你在主分支上
git checkout main

# 拉取最新更改
git pull upstream main

# 创建新分支
git checkout -b feature/your-feature-name
```

### 2. 开发你的功能

- 遵循项目的代码规范
- 为新功能编写测试
- 更新相关文档

### 3. 提交代码

```bash
# 添加更改
git add .

# 提交更改（使用清晰的提交信息）
git commit -m "feat: add new feature description"

# 推送分支
git push origin feature/your-feature-name
```

### 4. 创建 Pull Request

1. 在 GitHub 上创建 Pull Request
2. 填写 PR 模板
3. 等待代码审查

## 🏗️ 项目结构

```
py-ai-core/
├── py_ai_core/           # 主要源代码
│   ├── core/             # 核心功能模块
│   ├── models/           # 数据模型
│   ├── services/         # 业务逻辑服务
│   ├── tools/            # AI 工具
│   ├── mcp/              # MCP 协议实现
│   └── main.py           # 应用入口
├── tests/                # 测试代码
├── docs/                 # 文档
└── examples/             # 示例代码
```

## 📋 代码规范

### Python 代码风格

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范
- 使用 [Black](https://black.readthedocs.io/) 进行代码格式化
- 使用 [isort](https://pycqa.github.io/isort/) 整理导入语句

### 代码格式化

```bash
# 格式化代码
black py_ai_core/ tests/

# 整理导入
isort py_ai_core/ tests/
```

### 类型注解

- 尽可能使用类型注解
- 使用 `typing` 模块的类型提示
- 为函数参数和返回值添加类型注解

### 文档字符串

- 使用 Google 风格的文档字符串
- 为所有公共函数和类添加文档
- 包含参数说明、返回值说明和示例

```python
def process_data(data: List[str], limit: int = 100) -> Dict[str, Any]:
    """处理数据列表并返回统计结果.
    
    Args:
        data: 要处理的数据列表
        limit: 处理的最大数量，默认100
        
    Returns:
        包含统计信息的字典
        
    Raises:
        ValueError: 当数据为空时
        
    Example:
        >>> result = process_data(['a', 'b', 'c'])
        >>> print(result)
        {'count': 3, 'unique': 3}
    """
    pass
```

## 🧪 测试规范

### 测试要求

- 所有新功能必须包含测试
- 测试覆盖率应保持在 80% 以上
- 使用 `pytest` 作为测试框架

### 测试结构

```python
# tests/test_feature.py
import pytest
from py_ai_core.feature import some_function

class TestSomeFunction:
    def test_normal_case(self):
        """测试正常情况"""
        result = some_function("test")
        assert result == "expected"
    
    def test_edge_case(self):
        """测试边界情况"""
        with pytest.raises(ValueError):
            some_function("")
    
    @pytest.mark.asyncio
    async def test_async_function(self):
        """测试异步函数"""
        result = await some_async_function("test")
        assert result == "expected"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_feature.py

# 运行特定测试函数
pytest tests/test_feature.py::TestSomeFunction::test_normal_case

# 生成覆盖率报告
pytest --cov=py_ai_core --cov-report=html
```

## 📚 文档规范

### 文档要求

- 更新 README.md 中的相关部分
- 为新功能添加使用示例
- 更新 API 文档注释

### 文档格式

- 使用 Markdown 格式
- 包含代码示例
- 使用清晰的标题结构

## 🔍 代码审查

### 审查要点

- 代码质量和可读性
- 测试覆盖率
- 文档完整性
- 性能影响
- 安全性考虑

### 审查流程

1. 创建 Pull Request
2. 等待维护者审查
3. 根据反馈修改代码
4. 重新提交审查
5. 获得批准后合并

## 🐛 Bug 报告

### 报告格式

请在 GitHub Issues 中使用以下格式：

```markdown
**Bug 描述**
简要描述 bug 是什么

**重现步骤**
1. 第一步
2. 第二步
3. 第三步

**预期行为**
描述你期望看到的行为

**实际行为**
描述实际发生的行为

**环境信息**
- 操作系统：
- Python 版本：
- 项目版本：
- 其他相关信息：

**附加信息**
任何其他可能有用的信息
```

## 💡 功能建议

### 建议格式

```markdown
**功能描述**
简要描述你想要的功能

**使用场景**
描述这个功能的使用场景

**实现建议**
如果有的话，提供实现建议

**优先级**
高/中/低
```

## 📞 获取帮助

如果你在贡献过程中遇到问题：

1. 查看 [GitHub Issues](https://github.com/SolidFoundry/py-ai-core/issues)
2. 查看 [GitHub Discussions](https://github.com/SolidFoundry/py-ai-core/discussions)
3. 创建新的 Issue 或 Discussion

## 🎉 感谢

再次感谢你为 py-ai-core 项目做出贡献！你的参与让这个项目变得更好。

---

**注意**: 通过提交代码，你同意你的贡献将在 MIT 许可证下发布。
