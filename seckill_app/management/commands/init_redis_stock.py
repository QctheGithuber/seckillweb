# seckill_app/management/commands/init_redis_stock.py
from django.core.management.base import BaseCommand
from django.db import transaction
from seckill_app.models import Ticket # 导入模型
from seckill_app.redis_client import get_redis_connection, TICKET_STOCK_KEY_PREFIX, TICKET_GRABBED_USERS_KEY_PREFIX

class Command(BaseCommand):
    help = 'Initializes Redis stock based on Ticket models in the database and clears grabbed users'

    @transaction.atomic # 确保从数据库读取操作的原子性（如果需要）
    def handle(self, *args, **options):
        r = get_redis_connection()
        tickets = Ticket.objects.all() # 从数据库获取所有票品

        if not tickets:
            self.stdout.write(self.style.WARNING('No tickets found in the database. Please add tickets via Django Admin first.'))
            return

        self.stdout.write("Initializing Redis data based on database tickets...")

        initialized_count = 0
        for ticket in tickets:
            stock_key = TICKET_STOCK_KEY_PREFIX.format(ticket.id)
            grabbed_users_key = TICKET_GRABBED_USERS_KEY_PREFIX.format(ticket.id)
            initial_stock = ticket.initial_stock # 从模型获取初始库存

            # 设置初始库存到 Redis
            r.set(stock_key, initial_stock)

            # 清空已抢购用户列表 (Set)
            r.delete(grabbed_users_key)

            self.stdout.write(
                f"Ticket ID {ticket.id} ({ticket.name}): "
                f"Set Redis stock to {initial_stock}. Cleared grabbed users set."
            )
            initialized_count += 1

        self.stdout.write(self.style.SUCCESS(f'Redis data initialization complete for {initialized_count} tickets.'))