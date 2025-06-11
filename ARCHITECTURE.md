# 项目架构说明

## 架构原则

本项目采用了清晰的分层架构，遵循关注点分离原则：

- **API 层** - 只处理 HTTP 请求和响应
- **Service 层** - 处理业务逻辑
- **配置层** - 管理应用配置

## 目录结构

```
app/
├── __init__.py
├── main.py              # 应用入口点，只负责创建app实例
├── application.py       # 应用工厂，负责app配置和初始化
├── config.py           # 配置管理
├── dependencies.py     # 依赖注入
├── models.py          # Pydantic模型
└── api/               # API路由层
    ├── __init__.py
    ├── routes.py      # 路由聚合
    ├── health.py      # 健康检查路由
    ├── examples.py    # 示例API路由
    └── auth.py        # 认证相关路由

services/
├── __init__.py
└── example_service.py  # 业务逻辑服务
```

## 核心组件说明

### 1. 应用入口 (`app/main.py`)

```python
from app.application import create_app

app = create_app()
```

- 极简的入口文件
- 只负责创建应用实例
- 便于测试和部署

### 2. 应用工厂 (`app/application.py`)

```python
def create_app() -> FastAPI:
    """创建和配置FastAPI应用."""
```

- 使用工厂模式创建应用
- 集中管理中间件配置
- 集中管理异常处理
- 注册所有路由

### 3. API 路由层 (`app/api/`)

#### 路由组织原则：

- **按功能分组**: 不同功能的路由放在不同文件中
- **职责单一**: 每个路由文件只处理特定类型的端点
- **统一聚合**: `routes.py` 负责聚合所有路由

#### 路由文件：

- `health.py` - 系统健康检查和根路径
- `examples.py` - 示例业务 API
- `auth.py` - 认证和受保护的端点

### 4. Service 层 (`services/`)

- **纯业务逻辑**: 不包含 HTTP 相关代码
- **可复用**: 可以在不同的 API 端点中复用
- **易测试**: 独立于 API 层，便于单元测试

### 5. 配置层 (`app/config.py`)

- **环境变量管理**: 统一管理所有配置项
- **类型安全**: 使用 Pydantic 进行配置验证
- **环境隔离**: 支持不同环境的配置

## 优势

### 1. 清晰的分离关注点

- API 层只关心 HTTP 请求/响应
- Service 层只关心业务逻辑
- 配置层只关心应用设置

### 2. 可维护性

- 每个文件职责单一，容易理解和修改
- 新功能可以轻松添加新的路由文件
- 业务逻辑变更不会影响 API 结构

### 3. 可测试性

- Service 层可以独立进行单元测试
- API 层可以独立进行集成测试
- 配置层便于模拟不同环境

### 4. 可扩展性

- 新的 API 版本可以创建新的路由目录
- 新的服务可以轻松添加到 services 目录
- 中间件和配置可以统一管理

## 添加新功能

### 添加新的 API 端点：

1. 在 `app/api/` 中创建新的路由文件
2. 在 `app/api/routes.py` 中注册新路由
3. 如需要，在 `services/` 中创建对应的服务

### 添加新的配置项：

1. 在 `app/config.py` 中添加新的配置字段
2. 更新环境变量文件

### 添加新的业务逻辑：

1. 在 `services/` 中创建新的服务类
2. 在相应的 API 路由中调用服务

## 运行应用

```bash
uvicorn app.main:app --reload
```

应用将自动加载所有配置和路由。
