.PHONY: help install test lint format clean docker-build docker-run docker-stop

help: ## 显示帮助信息
	@echo "可用的命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 安装项目依赖
	pip install -e .

install-dev: ## 安装开发依赖
	pip install -e .[dev]

test: ## 运行测试
	pytest tests/ -v --cov=py_ai_core --cov-report=html --cov-report=term-missing

test-fast: ## 快速运行测试（不生成覆盖率报告）
	pytest tests/ -v

lint: ## 运行代码检查
	flake8 py_ai_core tests/
	black --check py_ai_core tests/
	isort --check-only py_ai_core tests/
	mypy py_ai_core/

format: ## 格式化代码
	black py_ai_core tests/
	isort py_ai_core tests/

clean: ## 清理临时文件
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +

docker-build: ## 构建Docker镜像
	docker-compose build

docker-run: ## 启动Docker服务
	docker-compose up -d

docker-stop: ## 停止Docker服务
	docker-compose down

docker-logs: ## 查看Docker日志
	docker-compose logs -f

docker-test: ## 在Docker中运行测试
	docker-compose --profile test run --rm test test

docker-test-cov: ## 在Docker中运行测试并生成覆盖率报告
	docker-compose --profile test run --rm test test --cov=py_ai_core --cov-report=html --cov-report=term-missing

docker-lint: ## 在Docker中运行代码检查
	docker-compose --profile test run --rm test lint

docker-format: ## 在Docker中格式化代码
	docker-compose --profile test run --rm test format

docker-shell: ## 进入Docker容器shell
	docker-compose --profile dev run --rm dev shell

docker-dev: ## 启动开发环境
	docker-compose --profile dev up -d

setup-pre-commit: ## 设置pre-commit钩子
	pre-commit install
	pre-commit install --hook-type commit-msg

run-pre-commit: ## 运行pre-commit检查
	pre-commit run --all-files

security-check: ## 运行安全检查
	pip install safety bandit
	safety check
	bandit -r py_ai_core/ -f json -o bandit-report.json

docker-security-check: ## 在Docker中运行安全检查
	docker-compose --profile test run --rm test bash -c "python -m safety check && python -m bandit -r py_ai_core/ -f json -o bandit-report.json"

docs: ## 生成文档
	@echo "文档生成功能待实现"

release: ## 发布新版本
	@echo "请手动更新版本号并创建git tag"

check-deps: ## 检查依赖更新
	pip install pip-review
	pip-review --interactive

update-deps: ## 更新依赖
	pip install pip-review
	pip-review --auto

# 开发工作流
dev-setup: ## 设置开发环境
	docker-compose up -d db
	@echo "等待数据库启动..."
	@sleep 10
	@echo "开发环境已准备就绪！"
	@echo "使用 'make docker-dev' 启动开发服务"
	@echo "使用 'make docker-test' 运行测试"

dev-test: ## 开发时快速测试
	docker-compose --profile test run --rm test test-fast

dev-lint: ## 开发时代码检查
	docker-compose --profile test run --rm test lint

dev-format: ## 开发时代码格式化
	docker-compose --profile test run --rm test format

.PHONY: help install test lint format clean docker-build docker-run docker-stop
