from django.contrib import admin

# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile
import uuid


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # 列表页显示的字段
    list_display = ['username', 'mobile', 'real_name', 'is_vip', 'vip_end_time',
                    'create_at', 'last_login_time', 'is_delete']

    # 可搜索的字段
    search_fields = ['username', 'mobile', 'real_name']

    # 列表过滤器
    list_filter = ['is_vip', 'is_delete', 'create_at', 'last_login_time']

    # 每页显示数量
    list_per_page = 20

    # 排序
    ordering = ['-create_at']

    # 在编辑页面显示字段
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'mobile', 'real_name', 'password')
        }),
        ('会员信息', {
            'fields': ('is_vip', 'vip_end_time')
        }),
        ('登录信息', {
            'fields': ('register_ip', 'last_login_ip', 'last_login_time')
        }),
        ('账户状态', {
            'fields': ('is_delete', 'deleted_at')
        }),
    )

    # 添加页面显示的字段
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'mobile', 'real_name', 'password1', 'password2'),
        }),
    )
