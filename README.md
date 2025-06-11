# FastAPI-UV Template

一个使用 uv 作为包管理器的现代化 FastAPI 项目模板，包含了最佳实践和常用功能。

## 特性

- 🚀 **FastAPI** - 高性能的现代 Web 框架
- 📦 **uv** - 极速的 Python 包管理器
- 🔧 **环境变量管理** - 使用 python-dotenv 和 pydantic-settings
- 🚦 **API 限流** - 使用 slowapi 实现请求频率限制
- 📚 **自动文档** - Swagger UI 和 ReDoc
- 🏗️ **分层架构** - API 和业务逻辑分离
- 🔐 **API Key 认证** - 示例认证机制
- 🌐 **CORS 支持** - 跨域资源共享配置
- 🛡️ **错误处理** - 统一的异常处理机制

## 项目结构

```
fastapi-uv/
├── app/                     # 主应用目录
│   ├── __init__.py
│   ├── main.py             # FastAPI 主应用
│   ├── config.py           # 配置管理
│   ├── dependencies.py     # 依赖项（限流、认证等）
│   └── models.py           # Pydantic 模型
├── services/               # 业务逻辑层
│   ├── __init__.py
│   └── example_service.py  # 示例服务
├── env.example            # 环境变量示例
├── pyproject.toml         # 项目配置
├── main.py                # 应用入口
└── README.md              # 项目说明
```

## 快速开始

### 1. 安装依赖

确保已安装 [uv](https://github.com/astral-sh/uv)：

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

uv pip install -e .
```

### 2. 使用统一管理脚本（推荐）

我们提供了统一的管理脚本 `fastapi.sh`：

```bash
# 给脚本执行权限
chmod +x fastapi.sh

# 查看帮助
./fastapi.sh --help

# 默认启动（本地后台，推荐）
./fastapi.sh start

# 查看状态
./fastapi.sh status

# 查看日志
./fastapi.sh logs --local

# 停止应用
./fastapi.sh stop
```

### 3. 传统启动方式

如果你更喜欢传统方式：

```bash
# 配置环境变量
cp env.example .env

# 使用 uvicorn 启动
python main.py

# 或直接使用 uvicorn
uvicorn app.main:app --reload
```

应用将在 http://localhost:8000 启动

## 🚀 后台启动工具

本项目支持多种后台启动方式：

1. **统一脚本管理**（推荐）- 一个脚本管理所有启动方式
2. **Gunicorn 守护进程** - 简单的后台启动
3. **Docker 容器** - 生产环境推荐
4. **Systemd 服务** - Linux 系统服务
5. **Supervisor** - 专业进程管理

详见：[USAGE.md](USAGE.md) 和 [DEPLOYMENT.md](DEPLOYMENT.md)

## API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

## 主要端点

- `GET /` - 欢迎页面
- `GET /health` - 健康检查
- `GET /api/v1/example` - 获取示例数据（带限流）
- `POST /api/v1/example` - 创建示例资源（带限流）
- `GET /api/v1/protected` - 需要 API Key 的受保护端点

## 环境变量说明

| 变量名              | 描述               | 默认值                                             |
| ------------------- | ------------------ | -------------------------------------------------- |
| APP_NAME            | 应用名称           | FastAPI UV Template                                |
| APP_VERSION         | 应用版本           | 0.1.0                                              |
| DEBUG               | 调试模式           | False                                              |
| HOST                | 服务器主机         | 0.0.0.0                                            |
| PORT                | 服务器端口         | 8000                                               |
| RELOAD              | 自动重载           | False                                              |
| API_PREFIX          | API 前缀           | /api/v1                                            |
| CORS_ORIGINS        | CORS 允许的源      | ["http://localhost:3000", "http://localhost:8000"] |
| RATE_LIMIT_REQUESTS | 限流请求数         | 100                                                |
| RATE_LIMIT_PERIOD   | 限流时间窗口（秒） | 60                                                 |

## 开发建议

1. **添加新的 API 端点**：在 `app/main.py` 中添加路由
2. **添加业务逻辑**：在 `services/` 目录下创建新的服务类
3. **添加数据模型**：在 `app/models.py` 中定义 Pydantic 模型
4. **添加依赖项**：在 `app/dependencies.py` 中创建可复用的依赖
5. **配置管理**：在 `app/config.py` 中添加新的配置项

## 测试 API

使用 curl 测试 API：

```bash
# 测试根端点
curl http://localhost:8000/

# 测试健康检查
curl http://localhost:8000/health

# 测试示例 GET 端点
curl http://localhost:8000/api/v1/example

# 测试示例 POST 端点
curl -X POST http://localhost:8000/api/v1/example \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "age": 30, "email": "john@example.com"}'

# 测试受保护端点（需要 API Key）
curl http://localhost:8000/api/v1/protected \
  -H "X-API-Key: your-api-key"
```

## License

MIT
