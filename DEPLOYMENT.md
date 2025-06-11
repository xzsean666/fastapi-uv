# FastAPI 后台启动部署指南

本项目提供了多种后台启动 FastAPI 应用的方法，适用于不同的部署场景。

## 🚀 统一管理脚本 (推荐)

我们提供了一个统一的管理脚本 `fastapi.sh`，集成了所有启动方式：

```bash
# 查看帮助
./fastapi.sh --help

# Docker方式启动
./fastapi.sh start --docker

# 本地前台启动
./fastapi.sh start --local

# 本地后台启动
./fastapi.sh start --local --daemon

# 停止服务
./fastapi.sh stop --docker     # 停止Docker
./fastapi.sh stop --local      # 停止本地服务

# 重启服务
./fastapi.sh restart --docker
./fastapi.sh restart --local --daemon

# 查看状态
./fastapi.sh status

# 查看日志
./fastapi.sh logs --docker     # Docker日志
./fastapi.sh logs --local      # 本地日志（交互式选择）
./fastapi.sh logs              # 查看所有日志

# 健康检查
./fastapi.sh health
```

## 🛠️ 各种启动方式详解

### 1. Gunicorn 守护进程 (推荐用于简单部署)

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

### 2. Docker 容器 (推荐用于生产环境)

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

### 3. Systemd 服务 (推荐用于 Linux 生产环境)

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

### 4. Supervisor 进程管理器

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

## 📊 性能对比

| 方式              | 启动速度   | 资源占用   | 管理复杂度 | 生产就绪   | 推荐场景   |
| ----------------- | ---------- | ---------- | ---------- | ---------- | ---------- |
| Gunicorn 守护进程 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐     | 开发/测试  |
| Docker            | ⭐⭐⭐     | ⭐⭐⭐     | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐ | 生产环境   |
| Systemd           | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ | Linux 生产 |
| Supervisor        | ⭐⭐⭐⭐   | ⭐⭐⭐⭐   | ⭐⭐⭐     | ⭐⭐⭐⭐   | 多服务管理 |

## 🔧 配置说明

### 环境变量

确保 `.env.production` 文件已正确配置:

```bash
cp env.production .env.production
# 编辑配置文件
nano .env.production
```

### 目录结构

```
fastapi-uv/
├── logs/              # 日志目录（自动创建）
├── pids/              # PID文件目录（自动创建）
├── start_local.sh     # 本地启动脚本
├── stop_local.sh      # 本地停止脚本
├── fastapi.service    # Systemd服务文件
└── supervisor_fastapi.conf  # Supervisor配置文件
```

## 🐛 故障排除

### 常见问题

1. **端口被占用**

   ```bash
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

2. **权限问题**

   ```bash
   chmod +x start_local.sh stop_local.sh
   ```

3. **日志查看**

   ```bash
   # Gunicorn守护进程
   tail -f logs/error.log

   # Docker
   docker-compose logs -f app

   # Systemd
   sudo journalctl -u fastapi -f

   # Supervisor
   sudo supervisorctl tail fastapi-app
   ```

4. **进程清理**

   ```bash
   # 查找相关进程
   ps aux | grep gunicorn

   # 清理僵尸进程
   pkill -f gunicorn
   ```

## 📈 监控和维护

### 健康检查

```bash
curl -f http://localhost:8000/health
```

### 日志轮转

建议配置 logrotate 来管理日志文件:

```bash
# /etc/logrotate.d/fastapi
/home/sean/git/fastapi-uv/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    notifempty
    create 644 sean sean
    postrotate
        # 重启应用以重新打开日志文件
        systemctl reload fastapi
    endscript
}
```

### 性能监控

- 使用 `htop` 监控系统资源
- 使用 `docker stats` 监控容器资源
- 配置 Prometheus + Grafana 进行详细监控

## 🚀 推荐部署流程

1. **开发阶段**: 使用 `./start_local.sh` 前台启动
2. **测试阶段**: 使用 `./start_local.sh --daemon` 后台启动
3. **生产阶段**: 使用 Docker 或 Systemd 服务
