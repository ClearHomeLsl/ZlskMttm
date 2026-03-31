# admin.py
from django.contrib import admin
from django.utils import timezone
from .models import FinanceNews


@admin.register(FinanceNews)
class FinanceNewsAdmin(admin.ModelAdmin):
    """金融新闻管理"""

    # 列表页显示的字段
    list_display = ['id', 'title', 'author', '_release_time', '_add_time']

    # 列表页可点击链接的字段
    list_display_links = ['id', 'title']

    # 列表页可编辑的字段
    list_editable = ['author']

    # 列表页筛选器（移除日期字段，暂时只用 author）
    list_filter = ['author']  # ← 修改：移除 release_time 和 add_time

    # 搜索字段
    search_fields = ['title', 'content', 'author']

    # 排序（改用 id 排序，避免日期问题）
    ordering = ['-id']  # ← 修改：改用 id 排序

    # 日期层级导航（暂时注释掉）
    # date_hierarchy = 'release_time'  # ← 注释掉这一行

    # 每页显示数量
    list_per_page = 20

    # 只读字段
    readonly_fields = ['id', '_add_time_display']  # ← 修改：使用自定义方法

    # 表单布局（字段分组）
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'content', 'author')
        }),
        ('链接信息', {
            'fields': ('news_link',),
            'classes': ('wide',)
        }),
        ('时间信息', {
            'fields': ('release_time', '_add_time_display'),  # ← 修改
            'classes': ('collapse',)
        }),
        ('系统信息', {
            'fields': ('id',),
            'classes': ('collapse',)
        }),
    )

    # ========== 安全的自定义方法 ==========

    def _release_time(self, obj):
        """安全地显示发布时间"""
        try:
            if obj.release_time:
                return obj.release_time.strftime("%Y-%m-%d %H:%M:%S")
            return '-'
        except Exception as e:
            return f'格式错误'

    _release_time.short_description = '发布时间'
    _release_time.admin_order_field = 'release_time'  # 允许排序

    def _add_time(self, obj):
        """安全地显示添加时间"""
        try:
            if obj.add_time:
                return obj.add_time.strftime("%Y-%m-%d %H:%M:%S")
            return '-'
        except Exception as e:
            return f'格式错误'

    _add_time.short_description = '添加时间'
    _add_time.admin_order_field = 'add_time'  # 允许排序

    def _add_time_display(self, obj):
        """详情页显示添加时间（只读）"""
        try:
            if obj.add_time:
                return obj.add_time.strftime("%Y-%m-%d %H:%M:%S")
            return '-'
        except Exception as e:
            return f'格式错误'

    _add_time_display.short_description = '添加时间'

    # 保存时自动填充 add_time
    def save_model(self, request, obj, form, change):
        if not obj.add_time:  # 新建时设置添加时间
            obj.add_time = timezone.now()
        super().save_model(request, obj, form, change)