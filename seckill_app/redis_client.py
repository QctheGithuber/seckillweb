# seckill_app/redis_client.py
import redis
from django.conf import settings

LUA_SCRIPT = """
local stock_key = KEYS[1]
local user_set_key = KEYS[2]
local user_id = ARGV[1]

if redis.call('SISMEMBER', user_set_key, user_id) == 1 then
    return 0
end

local stock = redis.call('GET', stock_key)
if not stock then
    return -2
end
if tonumber(stock) <= 0 then
    return -1
end

redis.call('DECR', stock_key)
redis.call('SADD', user_set_key, user_id)

return 1
"""
# 使用连接池
pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=settings.REDIS_DECODE_RESPONSES # 确保返回的是字符串
)

def get_redis_connection():
    """获取 Redis 连接"""
    return redis.StrictRedis(connection_pool=pool)

# 定义一些常用的 Key 前缀（好习惯）
TICKET_STOCK_KEY_PREFIX = "ticket:{}:stock" # 商品库存键 e.g., ticket:1:stock
TICKET_GRABBED_USERS_KEY_PREFIX = "ticket:{}:grabbed_users" # 记录抢到票的用户（用 Set）e.g., ticket:1:grabbed_users