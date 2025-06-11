# 更新日志

## v1.1.0 - 最新改进 (2024-12-11)

### 🎉 主要改进

#### 1. **智能默认参数**

- `./fastapi.sh start` - 默认使用 `--local --daemon`（本地后台启动）
- `./fastapi.sh stop` - 默认使用 `--local`（停止本地服务）
- `./fastapi.sh restart` - 默认使用 `--local --daemon`（重启本地后台服务）

#### 2. **动态端口配置**

- 端口现在从 `.env.production` 文件中的 `PORT` 变量读取
- 支持自定义端口，不再硬编码 8000
- 所有网络相关功能（健康检查、状态显示等）都使用动态端口

#### 3. **Docker 网络优化**

- `docker-compose.yml` 使用 `network_mode: host`
- 移除端口映射配置，使用主机网络模式
- 提升性能，减少网络开销

### 📝 使用方式对比

#### 旧版本

```bash
# 启动（需要指定参数）
./fastapi.sh start --local --daemon

# 停止（需要指定参数）
./fastapi.sh stop --local
```

#### 新版本

```bash
# 启动（简化命令）
./fastapi.sh start

# 停止（简化命令）
./fastapi.sh stop
```

### 🔧 技术改进

1. **环境变量加载**

   - 自动加载 `.env.production` 文件
   - 过滤注释行，避免解析错误
   - 设置默认值 `PORT=${PORT:-8000}`

2. **代码优化**

   - 在 `health_check()` 和 `show_status()` 中调用 `setup_environment()`
   - 确保所有端口相关功能都使用正确的端口值

3. **用户体验提升**
   - 更清晰的帮助信息
   - 显示默认行为说明
   - 自动提示使用的默认模式

### 🆕 新功能

- **智能模式检测**: 自动选择最合适的默认启动方式
- **端口自适应**: 根据配置文件自动调整端口
- **Host 网络模式**: Docker 容器使用主机网络，性能更优

---

## v1.0.0 - 初始版本

### ✨ 核心功能

- 统一脚本管理多种启动方式
- 支持 Docker 和本地启动
- 完整的日志管理
- 健康检查功能
- 进程状态监控

### 🛠️ 支持的启动方式

1. Gunicorn 守护进程
2. Docker 容器
3. Systemd 服务
4. Supervisor 进程管理器
