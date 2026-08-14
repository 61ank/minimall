# MiniMall 精简电商平台

精简 B2C 电商后端 REST API（Python + FastAPI）。核心购物闭环：商品浏览/搜索 → 购物车 → 下单 → 支付(模拟) → 订单履约，含库存防超卖与 Redis 缓存。

- 需求规格：见 [docs/requirements.md](docs/requirements.md)
- 训练日志：见 [docs/training-log.md](docs/training-log.md)

## 技术栈与关键决策

| 项 | 值 | 说明 |
|---|---|---|
| 语言/框架 | Python 3.14 + FastAPI | 用户选择学习 Python |
| 服务器 | uvicorn（ASGI 服务器） | FastAPI 不内置服务器，需 uvicorn 监听分发 |
| 依赖管理 | requirements.txt | 用户选择，简单直观 |
| 数据库/中间件 | MySQL + SQLAlchemy 2.0（同步）+ PyMySQL + Alembic（迁移） | 表设计见 docs/database.md |
| 缓存/搜索 | Redis（缓存，后续接入）、Elasticsearch（搜索，后期） | 需求见 docs/requirements.md |
| 远程仓库 | https://github.com/61ank/minimall（origin/main） | 已推送 |

## 目录结构

```
app/
  main.py        # 应用入口，create_app() 工厂
  core/          # config、database、logging、exceptions、security(密码哈希/JWT)
  routers/       # API 路由（health/auth/users/categories/products）
  services/      # 业务逻辑层（auth/users/products）
  models/        # ORM 模型层（用户/商品/购物车/订单等）
  schemas/       # Pydantic 请求/响应模型（auth/user/product/common）
  seed.py        # 开发种子数据
alembic/         # 数据库迁移（env.py 从 .env 读连接串）
tests/           # 测试（待填充）
docs/            # 需求规格、架构、数据库设计、训练日志
.claude/memory/  # 项目记忆（新会话先读 MEMORY.md）
```

## 常用命令

> 均需在项目根目录运行。未激活 venv 时，用 `.venv/Scripts/python.exe` 代替 `python`。

```bash
# 激活虚拟环境
source .venv/Scripts/activate      # Git Bash
.venv\Scripts\Activate.ps1         # PowerShell

# 安装/更新依赖
python -m pip install -r requirements.txt

# 启动服务（开发，改动自动重启）
python -m uvicorn app.main:app --reload
# 访问 http://127.0.0.1:8000/health ，接口文档 http://127.0.0.1:8000/docs

# 数据库迁移（Alembic）
python -m alembic revision --autogenerate -m "描述"   # 生成迁移
python -m alembic upgrade head                        # 应用迁移
python -m app.seed                                    # 插入开发种子数据

# 运行测试（阶段 9 完善）
python -m pytest
```

## 开发规范与约定

- **分层**：router → service →（repository 预留）。路由层不写业务逻辑，只做参数绑定与响应组装。
- **统一异常**：业务错误抛 `AppError(code, message, status_code)`，响应统一 `{"code": ..., "message": ...}`；未捕获异常统一 `500 INTERNAL_ERROR`，细节靠日志。
- **配置**：`app/core/config.py` 用 pydantic-settings 从 `.env` 读取；`.env` 不入库，模板为 `.env.example`。
- **应用工厂**：用 `create_app()` 创建实例，便于测试隔离。
- **命名**：包/模块小写下划线；类 PascalCase；函数/变量 snake_case；API 路径复数小写。
- **Git 提交**：提交前 `git status` + `git diff` 审查；提交信息用动词前缀（init/feat/fix/docs/chore/refactor/test）。

## 运行模型（为什么是 `uvicorn app.main:app`）

FastAPI 只定义接口（产出 `app` 对象），uvicorn 是 ASGI 服务器，负责监听端口、接收 HTTP 请求并交给 `app` 处理。启动命令 `uvicorn app.main:app` = "运行 `app/main.py` 里的 `app` 对象"。

## 注意事项

- **必须从项目根目录运行**，否则 `import app` 失败（直接运行 `app/main.py` 时搜索路径不含项目根）。
- 开发时用 `--reload` 自动重启。
- 需求细节的唯一归宿是 `docs/requirements.md`，不要在本文件或代码注释中复述需求。
- 项目记忆在 `.claude/memory/`，新会话先读 `MEMORY.md` 索引。
