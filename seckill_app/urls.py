# seckill_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ticket_list, name='ticket_list'), # 列表页
    path('grab/<int:ticket_id>/', views.grab_ticket, name='grab_ticket'), # 抢票动作
]