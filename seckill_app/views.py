# seckill_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages # 用于向用户显示反馈信息
from django.contrib.auth.decorators import login_required # 视图保护：要求用户登录
from django.db import transaction # 用于数据库事务，保证订单创建的原子性
from redis.exceptions import RedisError # 捕获 Redis 特定异常

from .models import Ticket, Order # 数据库模型
from .redis_client import ( # Redis 相关
    get_redis_connection,
    TICKET_STOCK_KEY_PREFIX,
    TICKET_GRABBED_USERS_KEY_PREFIX,
    LUA_SCRIPT,
    # LUA_SCRIPT_SHA # 如果使用了预加载
)

def ticket_list(request):
    """
    票品列表视图：
    - 从数据库获取票品基本信息 (名称, 描述等)
    - 从 Redis 获取实时库存
    - 渲染列表页面
    """
    r = get_redis_connection()
    db_tickets = Ticket.objects.all() # 获取所有数据库中的票品记录
    tickets_for_display = [] # 准备传递给模板的数据列表

    for ticket in db_tickets:
        stock = 0 # 默认库存为 0
        stock_key = TICKET_STOCK_KEY_PREFIX.format(ticket.id)
        try:
            redis_stock = r.get(stock_key) # 从 Redis 获取库存字符串
            if redis_stock is not None:
                stock = int(redis_stock) # 转换为整数
        except (ValueError, TypeError):
            # 如果 Redis 值不是有效数字，记录警告，库存仍为 0
            print(f"警告: Redis key '{stock_key}' 的值不是有效整数。")
        except RedisError as e:
            # 处理 Redis 连接或命令错误
            print(f"警告: 无法从 Redis 获取 key '{stock_key}' 的库存: {e}")
            messages.error(request, "无法获取部分票品库存信息，请稍后刷新。") # 可选：给用户提示

        tickets_for_display.append({
            'id': ticket.id,
            'name': ticket.name,
            'description': ticket.description,
            'stock': stock, # 使用从 Redis 获取的实时库存
        })

    context = {'tickets': tickets_for_display}
    return render(request, 'seckill_app/ticket_list.html', context)

@login_required # 关键：此视图需要用户登录才能访问
@transaction.atomic # 关键：将数据库操作包裹在事务中
def grab_ticket(request, ticket_id):
    """
    处理抢票请求的视图 (只接受 POST 请求):
    1. 验证用户是否已登录 (由 @login_required 处理)
    2. 获取票品对象
    3. 执行 Redis Lua 脚本进行原子性库存检查与扣减
    4. 如果 Redis 操作成功，则在数据库中创建订单记录
    5. 根据结果向用户显示消息并重定向
    """
    if request.method != 'POST':
        messages.error(request, "无效的请求方式。")
        return redirect(reverse('ticket_list'))

    user = request.user # 获取当前登录的用户对象
    ticket = get_object_or_404(Ticket, pk=ticket_id) # 尝试获取票品，若不存在则返回 404

    r = get_redis_connection()
    stock_key = TICKET_STOCK_KEY_PREFIX.format(ticket.id)
    grabbed_users_key = TICKET_GRABBED_USERS_KEY_PREFIX.format(ticket.id)
    user_id_str = str(user.id) # Lua 脚本需要字符串类型的用户 ID

    try:
        # --- 执行 Lua 脚本 ---
        # 优先尝试 EVALSHA (如果预加载了脚本)
        # if LUA_SCRIPT_SHA:
        #     try:
        #         result = r.evalsha(LUA_SCRIPT_SHA, 2, stock_key, grabbed_users_key, user_id_str)
        #     except redis.exceptions.NoScriptError:
        #         # 如果 SHA 失效 (Redis 重启等)，回退到 EVAL
        #         print("Lua script SHA not found, falling back to EVAL.")
        #         result = r.eval(LUA_SCRIPT, 2, stock_key, grabbed_users_key, user_id_str)
        # else:
        #     # 如果没有预加载，直接使用 EVAL
        #     result = r.eval(LUA_SCRIPT, 2, stock_key, grabbed_users_key, user_id_str)

        # 为简化，这里始终使用 EVAL (性能略低于 EVALSHA)
        result = r.eval(LUA_SCRIPT, 2, stock_key, grabbed_users_key, user_id_str)
        result = int(result) # Lua 返回的是数字，确保转为 Python 整数

        # --- 根据 Lua 返回结果处理 ---
        if result == 1: # 抢购成功
            # Redis 操作成功，现在尝试在数据库中创建订单
            # 使用 get_or_create 避免因意外重试导致重复创建订单
            # (unique_together 约束也会提供数据库层面的保护)
            order, created = Order.objects.get_or_create(
                user=user,
                ticket=ticket,
                # defaults={} # 如果有需要在创建时设置的默认值
            )
            if created:
                messages.success(request, f"恭喜您！成功抢到票品「{ticket.name}」！订单已生成。")
            else:
                # 虽然 Lua 应该先返回 0，但作为健壮性检查，处理此情况
                messages.warning(request, f"您已经成功抢购过票品「{ticket.name}」，无需重复操作。")

        elif result == 0: # 用户已抢过
            messages.warning(request, f"您已经抢购过票品「{ticket.name}」了，请勿重复抢购。")

        elif result == -1: # 库存不足
            messages.error(request, f"非常抱歉，票品「{ticket.name}」已被抢光！")

        elif result == -2: # Redis 中票品库存键不存在
            messages.error(request, f"系统错误：票品「{ticket.name}」的库存信息异常，请稍后再试或联系管理员。")
            # 此情况可能需要管理员运行 init_redis_stock 命令
            print(f"错误：尝试抢购票品 ID {ticket.id}，但 Redis key '{stock_key}' 不存在。")
        else:
            # 未预期的 Lua 返回值
            messages.error(request, "发生未知错误，请稍后重试。")
            print(f"错误：Lua 脚本返回未预期值 {result} (Ticket ID: {ticket.id}, User ID: {user.id})")

    except RedisError as e:
        # 处理 Redis 连接错误、命令错误等
        messages.error(request, f"系统繁忙，请稍后重试。(Redis 错误)")
        print(f"Redis 错误 (Ticket ID: {ticket.id}, User ID: {user.id}): {e}")
    except Exception as e:
        # 处理其他潜在异常 (如数据库写入失败 - @transaction.atomic 会回滚)
        messages.error(request, f"系统发生内部错误，请稍后重试。")
        print(f"抢票视图内部错误 (Ticket ID: {ticket.id}, User ID: {user.id}): {e}")
        # 注意：如果这里发生异常，因为有 @transaction.atomic，数据库写入会被回滚

    # 无论成功失败，都重定向回列表页
    return redirect(reverse('ticket_list'))