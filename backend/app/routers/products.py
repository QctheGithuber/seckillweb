from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from ..core.database import get_db
from ..core.redis import get_redis
from ..models.models import Product, Order
from typing import List
from pydantic import BaseModel
import logging
from sqlalchemy.exc import SQLAlchemyError
from ..core.database import get_db
from ..core.redis import get_redis
from ..models.models import Product, Order

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

router = APIRouter()

class ProductResponse(BaseModel):
    id: int
    name: str
    count: int

    class Config:
        from_attributes = True

@router.get("/products", response_model=List[ProductResponse])
async def get_products(db: AsyncSession = Depends(get_db)):
    stmt = select(Product).order_by(Product.id)
    result = await db.execute(stmt)
    products = result.scalars().all()
    return products

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    redis, _ = await get_redis()
    cached_product = await redis.get(f"cache:product:{product_id}")
    
    if cached_product:
        return ProductResponse.parse_raw(cached_product)
    
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    await redis.set(f"cache:product:{product_id}", product.json(), ex=3600)
    return product

@router.post("/flashsale/{user_id}/{product_id}")
async def flash_sale(
    user_id: int,
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        # 1. 在每次请求中获取 Redis 实例和已加载脚本的 SHA
        redis, script_sha = await get_redis()
        logger.debug(f"获取Redis连接成功，script_sha: {script_sha}")

        stock_key = f"stock:product:{product_id}"
        flag_key = f"order:flag:{user_id}:{product_id}"
        logger.debug(f"Redis keys - stock_key: {stock_key}, flag_key: {flag_key}")

        # 2. 检查商品是否存在于数据库
        stmt = select(Product).where(Product.id == product_id)
        result = await db.execute(stmt)
        product = result.scalar_one_or_none()
        if not product:
            logger.error(f"商品不存在: product_id={product_id}")
            raise HTTPException(status_code=404, detail="商品不存在")
        logger.debug(f"商品信息: {product.__dict__}")

        # 3. 如果 Redis 中还没初始化库存，就写入数据库中的初始库存
        if not await redis.exists(stock_key):
            logger.debug(f"初始化Redis库存: {product.count}")
            await redis.set(stock_key, product.count)

        # 4. 执行秒杀 Lua 脚本
        try:
            logger.debug("开始执行秒杀脚本")
            res = await redis.evalsha(
                script_sha,
                2,
                stock_key,
                flag_key
            )
            logger.debug(f"秒杀脚本执行结果: {res}")
        except Exception as e:
            logger.error(f"执行秒杀脚本失败：{str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"秒杀服务内部错误: {str(e)}")

        if res == 0:
            logger.info(f"库存不足: product_id={product_id}")
            raise HTTPException(status_code=400, detail="库存不足")
        if res == -1:
            logger.info(f"重复下单: user_id={user_id}, product_id={product_id}")
            raise HTTPException(status_code=400, detail="请勿重复下单")

        # 5. 脚本返回 1，说明 Redis 端已经原子扣减库存并标记，接下来操作数据库
        try:
            logger.debug("开始数据库事务")
            # 5.1 在数据库中扣减库存
            upd = (
                update(Product)
                .where(Product.id == product_id, Product.count > 0)
                .values(count=Product.count - 1)
                .returning(Product.count)
            )
            upd_result = await db.execute(upd)
            new_count = upd_result.scalar_one_or_none()
            logger.debug(f"数据库更新结果: new_count={new_count}")
            
            if new_count is None:
                logger.error("数据库扣减库存失败")
                await redis.incr(stock_key)
                raise HTTPException(status_code=400, detail="库存不足")

            # 5.2 创建订单记录
            order = Order(user_id=user_id, product_id=product_id)
            db.add(order)
            logger.debug(f"创建订单记录: user_id={user_id}, product_id={product_id}")

            # 提交事务
            await db.commit()
            logger.debug("数据库事务提交成功")

            # 6. 更新 Redis 缓存中的商品信息
            product.count = new_count
            await redis.set(
                f"cache:product:{product_id}",
                ProductResponse.from_orm(product).json(),
                ex=3600
            )
            logger.debug("更新Redis缓存成功")

            logger.info(f"秒杀成功：user_id={user_id} product_id={product_id}")
            return {"status": "success", "message": "抢购成功"}

        except SQLAlchemyError as e:
            logger.error(f"数据库事务失败: {str(e)}", exc_info=True)
            await db.rollback()
            await redis.incr(stock_key)
            raise HTTPException(status_code=500, detail="下单失败，请稍后重试")
            
    except HTTPException:
        # 直接重新抛出HTTPException，不进行额外处理
        raise
    except Exception as e:
        logger.error(f"秒杀过程发生未知错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="系统错误，请稍后重试")