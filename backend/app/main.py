from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import products
from .core.database import engine
from .models import models

app = FastAPI(title="秒杀系统")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(products.router, prefix="/api")

@app.on_event("startup")
async def startup():
    # 创建数据库表
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all) 