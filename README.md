# 票务秒杀系统

一个基于 FastAPI + Vue 3 的简单票务秒杀系统，实现了基本的秒杀功能，包括库存控制、防重复下单等特性。

## 技术栈

### 后端
- FastAPI
- SQLAlchemy (异步)
- PostgreSQL
- Redis + Lua
- Alembic

### 前端
- Vue 3
- TypeScript
- Vite
- Element Plus
- Pinia
- Vue Router

## 系统架构

### 数据库设计
- users: 用户表
- products: 商品表
- orders: 订单表

### Redis 设计
- 商品缓存: `cache:product:{product_id}`
- 库存控制: `stock:product:{product_id}`
- 防重复下单: `order:flag:{user_id}:{product_id}`

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+

### 后端启动

1. 进入后端目录：
```bash
cd backend
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
echo "DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost/seckill
REDIS_URL=redis://localhost" > .env
```

4. 创建数据库：
```bash
createdb seckill
```

5. 执行数据库迁移：
```bash
alembic upgrade head
```

6. 启动服务：
```bash
uvicorn app.main:app --reload
```

### 前端启动

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

## 测试系统

1. 创建测试数据：
```sql
INSERT INTO users (username) VALUES ('test_user');
INSERT INTO products (name, count) VALUES ('测试商品', 100);
```

2. 访问前端页面：
- 商品列表：http://localhost:5173/products
- 商品详情：http://localhost:5173/products/1

3. 使用 API 测试：
```bash
curl -X POST "http://localhost:8000/api/flashsale/1/1"
```

## 项目结构

```
.
├── backend/                # 后端项目
│   ├── app/               # 应用代码
│   │   ├── core/         # 核心配置
│   │   ├── models/       # 数据模型
│   │   └── routers/      # 路由处理
│   ├── alembic/          # 数据库迁移
│   └── requirements.txt   # 依赖管理
│
└── frontend/              # 前端项目
    ├── src/              # 源代码
    │   ├── api/         # API 接口
    │   ├── components/  # 组件
    │   ├── stores/      # 状态管理
    │   └── views/       # 页面
    └── package.json     # 依赖管理
```

## 主要功能

1. 商品管理
   - 商品列表展示
   - 商品详情查看
   - 库存管理

2. 秒杀功能
   - 库存控制
   - 防重复下单
   - 异步订单处理

3. 用户界面
   - 响应式设计
   - 实时反馈
   - 友好的交互体验

## 注意事项

1. 确保 PostgreSQL 和 Redis 服务已启动
2. 后端默认运行在 http://localhost:8000
3. 前端默认运行在 http://localhost:5173
4. 测试时使用固定的用户 ID 1 进行秒杀操作

## 开发计划

- [ ] 添加用户认证
- [ ] 实现订单管理
- [ ] 添加商品管理后台
- [ ] 优化秒杀性能
- [ ] 添加监控和日志
