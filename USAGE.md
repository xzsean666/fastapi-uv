# FastAPI 使用指南

## 🚀 快速开始

使用统一管理脚本 `fastapi.sh` 来管理你的 FastAPI 应用：

```bash
# 给脚本执行权限（首次使用）
chmod +x fastapi.sh

# 查看帮助
./fastapi.sh --help
```

## ⭐ 常用命令

### 启动应用

```bash
# 默认启动（本地后台）- 最简单的方式！
./fastapi.sh start

# 本地前台启动（用于调试）
./fastapi.sh start --local

# Docker 启动（推荐用于生产）
./fastapi.sh start --docker
```

### 停止应用

```bash
# 默认停止（本地应用）- 最简单的方式！
./fastapi.sh stop

# 停止 Docker 应用
./fastapi.sh stop --docker
```

### 查看状态

```bash
# 查看所有状态
./fastapi.sh status
```

### 查看日志

```bash
# 查看本地日志（交互式选择）
./fastapi.sh logs --local

# 查看 Docker 日志
./fastapi.sh logs --docker

# 查看所有日志概览
./fastapi.sh logs
```

### 健康检查

```bash
# 检查应用是否正常运行
./fastapi.sh health
```

### 重启应用

```bash
# 默认重启（本地后台）
./fastapi.sh restart

# 重启 Docker 应用
./fastapi.sh restart --docker
```

## 📊 应用访问

应用启动后，可以通过以下地址访问（端口从 `.env.production` 文件读取，默认 8000）：

- **主页**: http://localhost:${PORT}
- **健康检查**: http://localhost:${PORT}/health
- **API 文档**: http://localhost:${PORT}/docs

## 🔧 其他后台启动工具

### 1. Systemd 服务（推荐用于生产环境）

```bash
# 安装系统服务
sudo cp fastapi.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi

# 管理服务
sudo systemctl status fastapi
sudo systemctl stop fastapi
sudo systemctl restart fastapi
```

### 2. Supervisor 进程管理器

```bash
# 安装 supervisor
sudo apt-get install supervisor

# 配置服务
sudo cp supervisor_fastapi.conf /etc/supervisor/conf.d/
sudo supervisorctl reread
sudo supervisorctl update

# 管理服务
sudo supervisorctl start fastapi-app
sudo supervisorctl status fastapi-app
sudo supervisorctl stop fastapi-app
```

## 🐛 故障排除

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

## 📈 性能监控

```bash
# 查看系统资源使用
htop

# 查看应用进程
./fastapi.sh status

# 查看 Docker 资源使用
docker stats

# 实时查看日志
./fastapi.sh logs --local
```

## 🔄 工作流推荐

### 开发阶段

```bash
# 前台启动，方便调试
./fastapi.sh start --local
```

### 测试阶段

```bash
# 后台启动，释放终端（默认方式）
./fastapi.sh start

# 查看状态
./fastapi.sh status

# 查看日志
./fastapi.sh logs --local
```

### 生产阶段

```bash
# Docker 方式部署
./fastapi.sh start --docker

# 或者使用 systemd 服务
sudo systemctl start fastapi
```

---

💡 **提示**: 使用 `./fastapi.sh --help` 随时查看完整的命令说明！
