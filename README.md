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
│   ├── application.py      # 应用工厂，负责app配置和初始化
│   ├── config.py           # 配置管理
│   ├── dependencies.py     # 依赖项（限流、认证等）
│   ├── models.py           # Pydantic 模型
│   └── api/                # API路由层
│       ├── __init__.py
│       ├── routes.py       # 路由聚合
│       ├── health.py       # 健康检查路由
│       ├── examples.py     # 示例API路由
│       └── auth.py         # 认证相关路由
├── services/               # 业务逻辑层
│   ├── __init__.py
│   └── example_service.py  # 示例服务
├── env.example            # 环境变量示例
├── pyproject.toml         # 项目配置
├── fastapi.sh             # 统一管理脚本
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

## 使用指南

### ⭐ 常用命令

#### 启动应用

```bash
# 默认启动（本地后台）- 最简单的方式！
./fastapi.sh start

# 本地前台启动（用于调试）
./fastapi.sh start --local

# Docker 启动（推荐用于生产）
./fastapi.sh start --docker
```

#### 停止应用

```bash
# 默认停止（本地应用）- 最简单的方式！
./fastapi.sh stop

# 停止 Docker 应用
./fastapi.sh stop --docker
```

#### 查看状态

```bash
# 查看所有状态
./fastapi.sh status
```

#### 查看日志

```bash
# 查看本地日志（交互式选择）
./fastapi.sh logs --local

# 查看 Docker 日志
./fastapi.sh logs --docker

# 查看所有日志概览
./fastapi.sh logs
```

#### 健康检查

```bash
# 检查应用是否正常运行
./fastapi.sh health
```

#### 重启应用

```bash
# 默认重启（本地后台）
./fastapi.sh restart

# 重启 Docker 应用
./fastapi.sh restart --docker
```

### 📊 应用访问

应用启动后，可以通过以下地址访问（端口从 `.env.production` 文件读取，默认 8000）：

- **主页**: http://localhost:${PORT}
- **健康检查**: http://localhost:${PORT}/health
- **API 文档**: http://localhost:${PORT}/docs

### 🔄 工作流推荐

#### 开发阶段

```bash
# 前台启动，方便调试
./fastapi.sh start --local
```

#### 测试阶段

```bash
# 后台启动，释放终端（默认方式）
./fastapi.sh start

# 查看状态
./fastapi.sh status

# 查看日志
./fastapi.sh logs --local
```

#### 生产阶段

```bash
# Docker 方式部署
./fastapi.sh start --docker

# 或者使用 systemd 服务
sudo systemctl start fastapi
```

## 部署指南

### 🛠️ 各种启动方式详解

#### 1. Gunicorn 守护进程 (推荐用于简单部署)

```bash
# 后台启动（新方式）
./fastapi.sh start --local --daemon

# 停止应用
./fastapi.sh stop --local

# 查看日志
./fastapi.sh logs --local
```

**特点:**

- ✅ 简单易用，无需额外依赖
- ✅ 支持进程管理和日志记录
- ✅ 优雅启停
- ❌ 无自动重启功能
- ❌ 系统重启后需要手动启动

#### 2. Docker 容器 (推荐用于生产环境)

```bash
# 后台启动（新方式）
./fastapi.sh start --docker

# 停止应用
./fastapi.sh stop --docker

# 查看日志
./fastapi.sh logs --docker
```

**特点:**

- ✅ 容器化部署，环境一致性
- ✅ 自动重启
- ✅ 资源隔离
- ✅ 易于扩展和管理

#### 3. Systemd 服务 (推荐用于 Linux 生产环境)

```bash
# 安装服务
sudo cp fastapi.service /etc/systemd/system/
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start fastapi
sudo systemctl enable fastapi  # 开机自启

# 管理服务
sudo systemctl stop fastapi     # 停止
sudo systemctl restart fastapi  # 重启
sudo systemctl status fastapi   # 状态

# 查看日志
sudo journalctl -u fastapi -f
```

**特点:**

- ✅ 系统级服务管理
- ✅ 开机自启动
- ✅ 自动重启
- ✅ 完整的日志管理
- ✅ 安全权限控制

#### 4. Supervisor 进程管理器

```bash
# 安装 Supervisor
sudo apt-get install supervisor

# 复制配置文件
sudo cp supervisor_fastapi.conf /etc/supervisor/conf.d/

# 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 管理应用
sudo supervisorctl start fastapi-app    # 启动
sudo supervisorctl stop fastapi-app     # 停止
sudo supervisorctl restart fastapi-app  # 重启
sudo supervisorctl status fastapi-app   # 状态

# 查看日志
sudo supervisorctl tail fastapi-app
```

**特点:**

- ✅ 专业的进程管理
- ✅ 自动重启
- ✅ 丰富的配置选项
- ✅ Web 界面管理
- ✅ 多进程管理

### 📊 性能对比

| 方式              | 启动速度   | 资源占用   | 管理复杂度 | 生产就绪   | 推荐场景   |
| ----------------- | ---------- | ---------- | ---------- | ---------- | ---------- |
| Gunicorn 守护进程 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐     | 开发/测试  |
| Docker            | ⭐⭐⭐     | ⭐⭐⭐     | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐ | 生产环境   |
| Systemd           | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ | Linux 生产 |
| Supervisor        | ⭐⭐⭐⭐   | ⭐⭐⭐⭐   | ⭐⭐⭐     | ⭐⭐⭐⭐   | 多服务管理 |

## 项目架构

### 架构原则

本项目采用了清晰的分层架构，遵循关注点分离原则：

- **API 层** - 只处理 HTTP 请求和响应
- **Service 层** - 处理业务逻辑
- **配置层** - 管理应用配置

### 核心组件说明

#### 1. 应用入口 (`app/main.py`)

```python
from app.application import create_app

app = create_app()
```

- 极简的入口文件
- 只负责创建应用实例
- 便于测试和部署

#### 2. 应用工厂 (`app/application.py`)

```python
def create_app() -> FastAPI:
    """创建和配置FastAPI应用."""
```

- 使用工厂模式创建应用
- 集中管理中间件配置
- 集中管理异常处理
- 注册所有路由

#### 3. API 路由层 (`app/api/`)

**路由组织原则：**

- **按功能分组**: 不同功能的路由放在不同文件中
- **职责单一**: 每个路由文件只处理特定类型的端点
- **统一聚合**: `routes.py` 负责聚合所有路由

**路由文件：**

- `health.py` - 系统健康检查和根路径
- `examples.py` - 示例业务 API
- `auth.py` - 认证和受保护的端点

#### 4. Service 层 (`services/`)

- **纯业务逻辑**: 不包含 HTTP 相关代码
- **可复用**: 可以在不同的 API 端点中复用
- **易测试**: 独立于 API 层，便于单元测试

#### 5. 配置层 (`app/config.py`)

- **环境变量管理**: 统一管理所有配置项
- **类型安全**: 使用 Pydantic 进行配置验证
- **环境隔离**: 支持不同环境的配置

### 架构优势

#### 1. 清晰的分离关注点

- API 层只关心 HTTP 请求/响应
- Service 层只关心业务逻辑
- 配置层只关心应用设置

#### 2. 可维护性

- 每个文件职责单一，容易理解和修改
- 新功能可以轻松添加新的路由文件
- 业务逻辑变更不会影响 API 结构

#### 3. 可测试性

- Service 层可以独立进行单元测试
- API 层可以独立进行集成测试
- 配置层便于模拟不同环境

#### 4. 可扩展性

- 新的 API 版本可以创建新的路由目录
- 新的服务可以轻松添加到 services 目录
- 中间件和配置可以统一管理

## 开发建议

### 添加新功能

#### 添加新的 API 端点：

1. 在 `app/api/` 中创建新的路由文件
2. 在 `app/api/routes.py` 中注册新路由
3. 如需要，在 `services/` 中创建对应的服务

#### 添加新的配置项：

1. 在 `app/config.py` 中添加新的配置字段
2. 更新环境变量文件

#### 添加新的业务逻辑：

1. 在 `services/` 中创建新的服务类
2. 在相应的 API 路由中调用服务

### 测试 API

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

## 故障排除

### 常见问题

1. **端口被占用**

   ```bash
   # 查看占用端口的进程
   sudo lsof -i :8000

   # 或使用统一脚本查看状态
   ./fastapi.sh status
   ```

2. **应用无法启动**

   ```bash
   # 查看详细日志
   ./fastapi.sh logs --local
   ```

3. **权限问题**

   ```bash
   # 确保脚本有执行权限
   chmod +x fastapi.sh
   ```

4. **环境配置问题**

   ```bash
   # 检查环境文件
   ls -la .env.production

   # 如果不存在，脚本会自动创建
   ./fastapi.sh start --local --daemon
   ```

## 更新日志

### v1.1.0 - 最新改进 (2024-12-11)

#### 🎉 主要改进

- **智能默认参数**: `./fastapi.sh start` 默认使用本地后台启动
- **动态端口配置**: 端口从 `.env.production` 文件中的 `PORT` 变量读取
- **Docker 网络优化**: 使用 `network_mode: host`，提升性能

#### 📝 使用方式对比

**旧版本**:

```bash
./fastapi.sh start --local --daemon  # 需要指定参数
./fastapi.sh stop --local            # 需要指定参数
```

**新版本**:

```bash
./fastapi.sh start   # 简化命令
./fastapi.sh stop    # 简化命令
```

#### 🔧 技术改进

1. **环境变量加载**: 自动加载 `.env.production` 文件
2. **代码优化**: 统一端口配置管理
3. **用户体验提升**: 更清晰的帮助信息和默认行为

#### 🆕 新功能

- **智能模式检测**: 自动选择最合适的默认启动方式
- **端口自适应**: 根据配置文件自动调整端口
- **Host 网络模式**: Docker 容器使用主机网络，性能更优

### v1.0.0 - 初始版本

#### ✨ 核心功能

- 统一脚本管理多种启动方式
- 支持 Docker 和本地启动
- 完整的日志管理
- 健康检查功能
- 进程状态监控

#### 🛠️ 支持的启动方式

1. Gunicorn 守护进程
2. Docker 容器
3. Systemd 服务
4. Supervisor 进程管理器

## License

MIT
