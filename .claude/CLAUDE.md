# 项目规范

## 项目概况
FastAPI 示例项目，Python 3.13+，使用 uv 管理依赖。

## 包管理
- 统一使用 `uv`，禁止使用 pip/poetry
- 添加依赖：`uv add <package>`，开发依赖：`uv add --dev <package>`
- 运行：`uv run fastapi dev app/main.py`

## 技术栈
- **Web 框架**：FastAPI（async-first）
- **ORM**：SQLModel（SQLAlchemy + Pydantic 合体）
- **数据库**：PostgreSQL 生产环境，asyncpg 驱动；开发可用 SQLite + aiosqlite
- **迁移**：Alembic
- **密码哈希**：pwdlib[argon2]，不用 passlib/bcrypt
- **签名/Cookie**：itsdangerous，不用 PyJWT
- **缓存/限流**：Redis（redis-py asyncio）
- **配置**：pydantic-settings（BaseSettings），支持 .env 文件

## 架构分层
```
models → schemas → crud → api
```
不跨层直接操作，crud 层负责所有数据库读写。

## 代码风格
- **全面 async**：所有 handler 和数据库操作必须 async/await
- **极简 `__init__.py`**：只有 `app/__init__.py` 一个，其他目录不建
- **不过度设计**：只实现当前需求，不为未来写抽象
- **不加多余注释**：只有逻辑不自明时才加，不加 docstring 到未改动函数

## Schema 命名
- 后缀统一：`Base` / `Create` / `Read` / `Update`
- 对外 API 只暴露 `public_id`（UUID），不暴露整数主键

## 安全规范
- 所有写接口（POST/PUT/DELETE）必须验证 CSRF
- 用户敏感数据（API key）存签名 httponly cookie，不入库
- 系统 API key 存数据库，不存 .env

## 目录结构
```
app/
  __init__.py          # 唯一的 __init__.py
  main.py              # FastAPI app 实例
  core/
    config.py          # Settings（BaseSettings）
    database.py        # engine、session_factory、get_session
    lifespan.py        # @asynccontextmanager lifespan
    logger.py          # setup_logger()
  {domain}/
    models.py          # SQLModel table models
    schemas.py         # Pydantic schemas（Create/Read/Update）
    crud.py            # 异步 CRUD 函数
    api.py             # APIRouter
```

## 关键约定
- `Settings` 必须继承 `pydantic_settings.BaseSettings`，支持环境变量覆盖
- `lifespan` 必须用 `@asynccontextmanager` 装饰
- `setup_logger()` 在 lifespan 启动时调用
- `get_session` 通过 `request.state.session_factory` 获取，作为 FastAPI Depends 使用
