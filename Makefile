.PHONY: help build up down restart logs clean test

# 默认目标
help:
	@echo "中国A股量化交易系统 - Docker管理命令"
	@echo ""
	@echo "开发环境命令:"
	@echo "  make build          - 构建所有Docker镜像"
	@echo "  make up             - 启动所有服务"
	@echo "  make down           - 停止所有服务"
	@echo "  make restart        - 重启所有服务"
	@echo "  make logs           - 查看所有服务日志"
	@echo "  make logs-backend   - 查看后端日志"
	@echo "  make logs-frontend  - 查看前端日志"
	@echo "  make clean          - 清理所有容器和卷"
	@echo "  make test           - 运行测试"
	@echo ""
	@echo "生产环境命令:"
	@echo "  make prod-build     - 构建生产环境镜像"
	@echo "  make prod-up        - 启动生产环境"
	@echo "  make prod-down      - 停止生产环境"
	@echo "  make prod-logs      - 查看生产环境日志"
	@echo ""
	@echo "数据库命令:"
	@echo "  make db-migrate     - 运行数据库迁移"
	@echo "  make db-backup      - 备份数据库"
	@echo "  make db-restore     - 恢复数据库"
	@echo ""

# 开发环境
build:
	docker-compose build

up:
	docker-compose up -d
	@echo "服务已启动！"
	@echo "前端: http://localhost"
	@echo "后端API: http://localhost:8000"
	@echo "API文档: http://localhost:8000/docs"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

clean:
	docker-compose down -v
	docker system prune -f

test:
	docker-compose exec backend pytest
	docker-compose exec frontend npm run test

# 生产环境
prod-build:
	docker-compose -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.prod.yml up -d
	@echo "生产环境已启动！"

prod-down:
	docker-compose -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f

# 数据库操作
db-migrate:
	docker-compose exec backend alembic upgrade head

db-backup:
	docker-compose exec db pg_dump -U postgres quant_trading > backup/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "数据库备份完成"

db-restore:
	@read -p "输入备份文件名: " file; \
	docker-compose exec -T db psql -U postgres quant_trading < backup/$$file
	@echo "数据库恢复完成"

# 进入容器
shell-backend:
	docker-compose exec backend /bin/bash

shell-frontend:
	docker-compose exec frontend /bin/sh

shell-db:
	docker-compose exec db psql -U postgres quant_trading

# 健康检查
health:
	@echo "检查服务健康状态..."
	@docker-compose ps
