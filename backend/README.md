# 秒杀系统后端

## 环境要求

- Python 3.8+
- PostgreSQL 12+
- Redis 6+

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 创建 `.env` 文件：

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost/seckill
REDIS_URL=redis://localhost
```

2. 创建数据库：

```bash
sudo -u postgres createdb seckill
psql -h localhost -p 5432 -U postgres -d seckill -f backend/scripts/seed_data.sql
```

## 数据库迁移

```bash
# 初始化迁移
alembic init alembic

# 创建迁移脚本
alembic revision --autogenerate -m "initial"

# 执行迁移
alembic upgrade head
```

## 启动服务

```bash
uvicorn app.main:app --reload
```

## API 文档

启动服务后访问：http://localhost:8000/docs

## 测试秒杀

1. 创建测试用户和商品：

```sql
INSERT INTO users (username) VALUES ('test_user');
INSERT INTO products (name, count) VALUES ('测试商品', 100);
```

2. 使用 curl 测试秒杀：

```bash
curl -X POST "http://localhost:8000/api/flashsale/1/1"
``` 