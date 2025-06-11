#!/bin/bash
set -e

# 脚本信息
SCRIPT_NAME="FastAPI Manager"
VERSION="1.0.0"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# 显示帮助信息
show_help() {
    echo "🚀 $SCRIPT_NAME v$VERSION"
    echo ""
    echo "用法: $0 <command> [options]"
    echo ""
    echo "命令:"
    echo "  start          启动应用"
    echo "  stop           停止应用"
    echo "  restart        重启应用"
    echo "  status         查看状态"
    echo "  logs           查看日志"
    echo "  health         健康检查"
    echo ""
    echo "启动选项:"
    echo "  --docker, -d   使用Docker方式启动"
    echo "  --local, -l    使用本地方式启动（前台）"
    echo "  --daemon       本地后台启动（需配合--local）"
    echo ""
    echo "示例:"
    echo "  $0 start                    # 默认: 本地后台启动 (--local --daemon)"
    echo "  $0 stop                     # 默认: 停止本地服务 (--local)"
    echo "  $0 start --docker          # Docker方式启动"
    echo "  $0 start --local           # 本地前台启动"
    echo "  $0 start --local --daemon  # 本地后台启动"
    echo "  $0 stop --docker           # 停止Docker服务"
    echo "  $0 status                  # 查看所有状态"
    echo "  $0 logs --docker           # 查看Docker日志"
    echo "  $0 logs --local            # 查看本地日志"
    echo ""
}

# 检查依赖
check_dependencies() {
    local mode=$1
    
    if [[ "$mode" == "docker" ]]; then
        if ! command -v docker &> /dev/null; then
            print_error "Docker 未安装"
            exit 1
        fi
        if ! command -v docker-compose &> /dev/null; then
            print_error "Docker Compose 未安装"
            exit 1
        fi
    elif [[ "$mode" == "local" ]]; then
        if ! command -v uv &> /dev/null; then
            print_error "uv 未安装"
            exit 1
        fi
    fi
}

# 设置环境
setup_environment() {
    # 创建必要目录
    mkdir -p logs pids
    
    # 设置默认值
    PORT=${PORT:-8000}
    
    # 加载环境变量（如果文件存在）
    if [ -f ".env.production" ]; then
        print_info "加载环境配置文件 .env.production"
        # 更安全的环境变量加载：只加载有效的KEY=VALUE格式的行
        while IFS= read -r line; do
            # 跳过空行和注释行
            if [[ -n "$line" && ! "$line" =~ ^[[:space:]]*# ]]; then
                # 检查是否是有效的KEY=VALUE格式
                if [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then
                    export "$line"
                fi
            fi
        done < .env.production
    elif [ -f "env.production" ]; then
        print_info "未找到 .env.production，从 env.production 创建"
        # 更安全地复制和加载
        cp env.production .env.production
        print_warning "请编辑 .env.production 文件，修改密钥等配置项"
        # 重新调用自身来加载新创建的文件
        setup_environment
        return
    else
        print_info "使用默认配置（端口: $PORT）"
    fi
}

# Docker方式启动
start_docker() {
    print_info "使用 Docker + uv + gunicorn 启动应用"
    
    check_dependencies "docker"
    setup_environment
    
    print_info "构建 Docker 镜像..."
    docker-compose build
    
    print_info "启动服务..."
    docker-compose up -d
    
    # 等待服务启动
    print_info "等待服务启动..."
    sleep 5
    
    # 健康检查
    print_info "执行健康检查..."
    for i in {1..10}; do
        if curl -f http://localhost:${PORT}/health > /dev/null 2>&1; then
            print_success "应用启动成功！"
            print_info "🌐 访问地址: http://localhost:${PORT}"
            print_info "📊 健康检查: http://localhost:${PORT}/health"
            print_info "📜 查看日志: $0 logs --docker"
            return 0
        fi
        echo "等待中... ($i/10)"
        sleep 2
    done
    
    print_error "健康检查失败，查看日志："
    docker-compose logs app
    exit 1
}

# 本地方式启动
start_local() {
    local daemon_mode=$1
    
    check_dependencies "local"
    setup_environment
    
    # 环境变量已在 setup_environment 中加载
    
    if [[ "$daemon_mode" == "true" ]]; then
        print_info "使用 uv + gunicorn 后台启动应用"
        
        # 检查是否已经在运行
        if [ -f "pids/gunicorn.pid" ]; then
            PID=$(cat pids/gunicorn.pid)
            if ps -p $PID > /dev/null 2>&1; then
                print_error "应用已在运行 (PID: $PID)"
                print_info "使用 $0 stop --local 停止应用"
                exit 1
            else
                print_info "清理旧的PID文件..."
                rm -f pids/gunicorn.pid
            fi
        fi
        
        # 后台启动
        uv run gunicorn app.app:app \
            --workers 4 \
            --worker-class uvicorn.workers.UvicornWorker \
            --bind 0.0.0.0:${PORT} \
            --timeout 30 \
            --keep-alive 2 \
            --daemon \
            --pid pids/gunicorn.pid \
            --access-logfile logs/access.log \
            --error-logfile logs/error.log
        
        print_success "应用已在后台启动！"
        print_info "🌐 访问地址: http://localhost:${PORT}"
        print_info "📊 健康检查: http://localhost:${PORT}/health"
        print_info "📜 查看日志: $0 logs --local"
        print_info "🛑 停止应用: $0 stop --local"
        
        # 显示PID
        if [ -f "pids/gunicorn.pid" ]; then
            PID=$(cat pids/gunicorn.pid)
            print_info "🆔 进程ID: $PID"
        fi
    else
        print_info "使用 uv + gunicorn 前台启动应用"
        print_info "💡 按 Ctrl+C 停止应用"
        
        # 前台启动
        uv run gunicorn app.app:app \
            --workers 4 \
            --worker-class uvicorn.workers.UvicornWorker \
            --bind 0.0.0.0:${PORT} \
            --timeout 30 \
            --keep-alive 2 \
            --access-logfile - \
            --error-logfile -
    fi
}

# Docker方式停止
stop_docker() {
    print_info "停止 Docker FastAPI 应用..."
    docker-compose down
    print_success "Docker 应用已停止"
}

# 本地方式停止
stop_local() {
    print_info "停止本地 FastAPI 应用..."
    
    # 检查PID文件是否存在
    if [ ! -f "pids/gunicorn.pid" ]; then
        print_error "未找到PID文件，应用可能未在后台运行"
        print_info "使用 ps aux | grep gunicorn 查看是否有相关进程"
        exit 1
    fi
    
    # 读取PID
    PID=$(cat pids/gunicorn.pid)
    
    # 检查进程是否存在
    if ! ps -p $PID > /dev/null 2>&1; then
        print_error "进程 $PID 不存在，清理PID文件..."
        rm -f pids/gunicorn.pid
        exit 1
    fi
    
    print_info "终止进程 $PID..."
    
    # 尝试优雅停止
    kill -TERM $PID
    
    # 等待几秒
    sleep 3
    
    # 检查进程是否还在运行
    if ps -p $PID > /dev/null 2>&1; then
        print_warning "进程仍在运行，强制终止..."
        kill -KILL $PID
        sleep 1
    fi
    
    # 最终检查
    if ps -p $PID > /dev/null 2>&1; then
        print_error "无法终止进程 $PID"
        exit 1
    else
        print_success "应用已停止"
        rm -f pids/gunicorn.pid
    fi
}

# 查看状态
show_status() {
    setup_environment  # 确保端口变量已设置
    echo "📊 FastAPI 应用状态"
    echo "===================="
    
    # Docker状态
    echo ""
    echo "🐳 Docker 状态:"
    if docker-compose ps 2>/dev/null | grep -q "Up"; then
        print_success "Docker 容器正在运行"
        docker-compose ps
    else
        print_info "Docker 容器未运行"
    fi
    
    # 本地状态
    echo ""
    echo "💻 本地状态:"
    if [ -f "pids/gunicorn.pid" ]; then
        PID=$(cat pids/gunicorn.pid)
        if ps -p $PID > /dev/null 2>&1; then
            print_success "本地应用正在运行 (PID: $PID)"
            echo "进程信息:"
            ps -p $PID -o pid,ppid,cmd --no-headers
        else
            print_warning "PID文件存在但进程不存在，清理PID文件..."
            rm -f pids/gunicorn.pid
        fi
    else
        print_info "本地应用未在后台运行"
    fi
    
    # 端口状态
    echo ""
    echo "🔌 端口状态:"
    if lsof -i :${PORT} >/dev/null 2>&1; then
        print_success "端口 ${PORT} 正在使用"
        lsof -i :${PORT}
    else
        print_info "端口 ${PORT} 未被使用"
    fi
}

# 查看日志
show_logs() {
    local mode=$1
    
    if [[ "$mode" == "docker" ]]; then
        print_info "查看 Docker 日志..."
        docker-compose logs -f app
    elif [[ "$mode" == "local" ]]; then
        print_info "查看本地日志..."
        echo "选择要查看的日志:"
        echo "1) 访问日志 (logs/access.log)"
        echo "2) 错误日志 (logs/error.log)"
        echo "3) 同时查看两个日志"
        read -p "请选择 [1-3]: " choice
        
        case $choice in
            1)
                if [ -f "logs/access.log" ]; then
                    tail -f logs/access.log
                else
                    print_error "访问日志文件不存在"
                fi
                ;;
            2)
                if [ -f "logs/error.log" ]; then
                    tail -f logs/error.log
                else
                    print_error "错误日志文件不存在"
                fi
                ;;
            3)
                if [ -f "logs/access.log" ] && [ -f "logs/error.log" ]; then
                    tail -f logs/access.log logs/error.log
                else
                    print_error "日志文件不存在"
                fi
                ;;
            *)
                print_error "无效选择"
                exit 1
                ;;
        esac
    else
        print_info "查看所有可用日志..."
        echo ""
        echo "Docker 日志:"
        if docker-compose ps 2>/dev/null | grep -q "Up"; then
            docker-compose logs --tail=10 app
        else
            print_info "Docker 未运行"
        fi
        
        echo ""
        echo "本地日志:"
        if [ -f "logs/access.log" ]; then
            echo "最近的访问日志:"
            tail -5 logs/access.log
        fi
        if [ -f "logs/error.log" ]; then
            echo "最近的错误日志:"
            tail -5 logs/error.log
        fi
    fi
}

# 健康检查
health_check() {
    setup_environment  # 确保端口变量已设置
    print_info "执行健康检查..."
    
    if curl -f http://localhost:${PORT}/health > /dev/null 2>&1; then
        print_success "应用健康检查通过"
        echo "详细信息:"
        curl -s http://localhost:${PORT}/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:${PORT}/health
    else
        print_error "应用健康检查失败"
        print_info "请检查应用是否正在运行: $0 status"
        exit 1
    fi
}

# 重启应用
restart_app() {
    local mode=$1
    local daemon_mode=$2
    
    print_info "重启应用..."
    
    if [[ "$mode" == "docker" ]]; then
        stop_docker
        sleep 2
        start_docker
    elif [[ "$mode" == "local" ]]; then
        # 检查是否有运行的实例
        if [ -f "pids/gunicorn.pid" ]; then
            stop_local
            sleep 2
        fi
        start_local "$daemon_mode"
    else
        print_error "请指定重启模式: --docker 或 --local"
        exit 1
    fi
}

# 主函数
main() {
    local command=""
    local mode=""
    local daemon_mode="false"
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            start|stop|restart|status|logs|health)
                command="$1"
                shift
                ;;
            --docker|-d)
                mode="docker"
                shift
                ;;
            --local|-l)
                mode="local"
                shift
                ;;
            --daemon)
                daemon_mode="true"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_error "未知参数: $1"
                echo ""
                show_help
                exit 1
                ;;
        esac
    done
    
    # 检查是否提供了命令
    if [[ -z "$command" ]]; then
        show_help
        exit 1
    fi
    
    # 执行对应的命令
    case $command in
        start)
            # 如果没有指定模式，默认使用 --local --daemon
            if [[ -z "$mode" ]]; then
                mode="local"
                daemon_mode="true"
                print_info "使用默认模式: --local --daemon"
            fi
            
            if [[ "$mode" == "docker" ]]; then
                start_docker
            elif [[ "$mode" == "local" ]]; then
                start_local "$daemon_mode"
            fi
            ;;
        stop)
            # 如果没有指定模式，默认使用 --local
            if [[ -z "$mode" ]]; then
                mode="local"
                print_info "使用默认模式: --local"
            fi
            
            if [[ "$mode" == "docker" ]]; then
                stop_docker
            elif [[ "$mode" == "local" ]]; then
                stop_local
            fi
            ;;
        restart)
            # 如果没有指定模式，默认使用 --local --daemon
            if [[ -z "$mode" ]]; then
                mode="local"
                daemon_mode="true"
                print_info "使用默认模式: --local --daemon"
            fi
            restart_app "$mode" "$daemon_mode"
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$mode"
            ;;
        health)
            health_check
            ;;
        *)
            print_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@" 