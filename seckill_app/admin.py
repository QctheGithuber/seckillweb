# seckill_app/admin.py
from django.contrib import admin
from .models import Ticket, Order

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'initial_stock', 'current_redis_stock') # 添加显示 Redis 库存的方法
    search_fields = ('name',)

    def current_redis_stock(self, obj):
        """从 Redis 获取当前库存并在 Admin 中显示"""
        from .redis_client import get_redis_connection, TICKET_STOCK_KEY_PREFIX
        r = get_redis_connection()
        stock_key = TICKET_STOCK_KEY_PREFIX.format(obj.id)
        stock = r.get(stock_key)
        return stock if stock is not None else 'N/A (Not Initialized)'
    current_redis_stock.short_description = 'Redis 当前库存' # 列名

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ticket', 'order_time')
    list_filter = ('ticket', 'order_time')
    search_fields = ('user__username', 'ticket__name')
    readonly_fields = ('user', 'ticket', 'order_time') # 订单通常创建后不应修改

    def has_add_permission(self, request):
        # 禁止在 Admin 中手动添加订单
        return False

    def has_change_permission(self, request, obj=None):
         # 禁止在 Admin 中修改订单 (可以通过 readonly_fields 控制)
         return False # 或者更细粒度控制