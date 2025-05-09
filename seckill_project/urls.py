# seckill_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), # 添加 Django 认证 URL (login, logout, etc.)
    path('', include('seckill_app.urls')), # 应用的 URL
]