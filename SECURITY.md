# 安全政策

## 支持的版本

我们致力于为以下版本提供安全更新：

| 版本 | 支持状态 |
| ---- | -------- |
| 0.1.x | ✅ 支持 |

## 报告漏洞

我们非常重视安全问题。如果你发现了安全漏洞，请不要公开披露，而是通过以下方式私下报告：

### 报告方式

1. **GitHub Security Advisories** (推荐)
   - 访问项目的 [Security](https://github.com/SolidFoundry/py-ai-core/security) 页面
   - 点击 "Report a vulnerability"
   - 填写详细的安全报告

2. **邮件报告**
   - 发送邮件到 [studio.aethos@outlook.com]
   - 主题请包含 "[SECURITY]" 前缀
   - 详细描述漏洞情况

### 报告内容

请在安全报告中包含以下信息：

- 漏洞的详细描述
- 重现步骤
- 潜在影响评估
- 建议的修复方案（如果有）
- 你的联系方式（可选）

### 响应时间

- **严重漏洞** (Critical): 24小时内响应
- **高危漏洞** (High): 48小时内响应
- **中危漏洞** (Medium): 7天内响应
- **低危漏洞** (Low): 30天内响应

## 安全最佳实践

### 环境变量

- 永远不要在代码中硬编码敏感信息
- 使用 `.env` 文件管理环境变量
- 确保 `.env` 文件不被提交到版本控制系统

```bash
# 正确做法
export OPENAI_API_KEY="your-api-key"

# 错误做法
OPENAI_API_KEY = "your-api-key"  # 在代码中硬编码
```

### API 密钥管理

- 定期轮换 API 密钥
- 使用最小权限原则
- 监控 API 使用情况

### 数据库安全

- 使用强密码
- 限制数据库访问权限
- 定期备份数据
- 启用 SSL/TLS 连接

### 依赖管理

- 定期更新依赖包
- 使用 `pip audit` 检查已知漏洞
- 监控依赖包的安全公告

```bash
# 检查依赖包的安全漏洞
pip install safety
safety check

# 或者使用 pip-audit
pip install pip-audit
pip-audit
```

## 安全更新

### 发布流程

1. 安全漏洞被确认
2. 开发修复补丁
3. 内部测试验证
4. 发布安全更新
5. 发布安全公告

### 更新通知

- 安全更新会通过 GitHub Releases 发布
- 严重漏洞会发布安全公告
- 建议用户及时更新到最新版本

## 安全联系方式

- **安全邮箱**: [studio.aethos@outlook.com]
- **GitHub Security**: [Security Page](https://github.com/SolidFoundry/py-ai-core/security)
- **紧急联系**: [studio.aethos@outlook.com]

## 致谢

感谢所有负责任地报告安全漏洞的研究者和用户。你们的贡献帮助我们保持项目的安全性。

---

**重要提醒**: 如果你在生产环境中发现安全漏洞，请立即采取必要的防护措施，并尽快联系我们。
