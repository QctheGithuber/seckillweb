import aioredis
import os
from dotenv import load_dotenv
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost")

FLASH_SALE_SCRIPT = """
local stock = tonumber(redis.call('GET', KEYS[1]))          -- 获取商品库存数量
if not stock or stock <= 0 then return 0 end                -- 如果库存不存在或小于等于0，返回0
if redis.call('EXISTS', KEYS[2]) == 1 then return -1 end    -- 如果用户已经抢购过，返回-1
redis.call('DECR', KEYS[1])                                 -- 库存减1
redis.call('SET', KEYS[2], 1)                               -- 设置用户抢购标记
redis.call('EXPIRE', KEYS[2], 600)                          -- 设置标记10分钟后过期
return 1                                                    -- 抢购成功，返回1
"""

async def init_redis():
    try:
        logger.debug("正在连接Redis...")
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        logger.debug("Redis连接成功")
        
        logger.debug("正在加载Lua脚本...")
        script_sha = await redis.script_load(FLASH_SALE_SCRIPT)
        logger.debug(f"Lua脚本加载成功，SHA: {script_sha}")
        
        # 验证脚本是否正确加载
        try:
            logger.debug("验证Lua脚本...")
            result = await redis.evalsha(script_sha, 2, "test_stock", "test_flag")
            logger.debug(f"Lua脚本验证结果: {result}")
        except Exception as e:
            logger.error(f"Lua脚本验证失败: {str(e)}", exc_info=True)
            raise
            
        return redis, script_sha
    except Exception as e:
        logger.error(f"Redis初始化失败: {str(e)}", exc_info=True)
        raise

async def get_redis():
    try:
        redis, script_sha = await init_redis()
        return redis, script_sha
    except Exception as e:
        logger.error(f"获取Redis连接失败: {str(e)}", exc_info=True)
        raise 