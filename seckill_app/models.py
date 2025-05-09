# seckill_app/models.py
from django.db import models
from django.conf import settings # 用于引用 User 模型
from django.utils import timezone

class Ticket(models.Model):
    """票品信息模型"""
    name = models.CharField(max_length=100, verbose_name="票品名称")
    description = models.TextField(blank=True, verbose_name="描述")
    initial_stock = models.PositiveIntegerField(default=0, verbose_name="初始库存")
    # 可以添加其他字段，如价格、场次时间等

    def __str__(self):
        return f"{self.name} (ID: {self.id})"

    class Meta:
        verbose_name = "票品"
        verbose_name_plural = "票品"


class Order(models.Model):
    """订单模型，记录成功抢购的记录"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, # 使用 Django 内建的 User 模型
        on_delete=models.CASCADE, # 当用户删除时，其订单也删除（可根据业务调整）
        verbose_name="用户"
    )
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE, # 当票品删除时，相关订单也删除
        verbose_name="票品"
    )
    order_time = models.DateTimeField(default=timezone.now, verbose_name="下单时间")

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.ticket.name}"

    class Meta:
        verbose_name = "订单"
        verbose_name_plural = "订单"
        ordering = ['-order_time'] # 默认按下单时间降序排列
        unique_together = ('user', 'ticket') # 一个用户对一个票品只能下一单（业务约束）