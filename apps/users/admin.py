# admin.py - 简化版
from .models import *


from django.contrib import admin
from django.utils.html import format_html
from .models import GameSymbol, GameCenter, UserGameSignUp, PointRecord


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """用户信息管理（简化版）"""

    list_display = ['username', 'real_name', 'mobile', 'email', 'is_vip', 'point_level', 'user_stutas', 'create_at', 'vip_end_time', 'is_first_pay']
    list_filter = ['is_vip', 'user_stutas', 'point_level', 'create_at']
    search_fields = ['username', 'real_name', 'mobile', 'email']
    ordering = ['-create_at']
    list_per_page = 20

    readonly_fields = ['id', 'create_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'real_name', 'mobile', 'email', 'password')
        }),
        ('会员与积分', {
            'fields': ('is_vip', 'vip_end_time', 'point', 'point_level', "is_receive_vip", "is_vip_experience")
        }),
        ('状态信息', {
            'fields': ('user_stutas', 'is_delete')
        }),
        ('系统信息', {
            'fields': ('id', 'create_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['make_vip', 'ban_users']

    def make_vip(self, request, queryset):
        updated = queryset.update(is_vip=True, vip_end_time=timezone.now() + timezone.timedelta(days=365))
        self.message_user(request, f'已成功将 {updated} 个用户设为会员')

    make_vip.short_description = '设为会员'

    def ban_users(self, request, queryset):
        updated = queryset.update(user_stutas=2)
        self.message_user(request, f'已成功封禁 {updated} 个用户')

    ban_users.short_description = '封禁用户'

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data and obj.password:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


@admin.register(GameSymbol)
class GameSymbolAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_game']
    list_filter = ['is_game']
    search_fields = ['name']


@admin.register(GameCenter)
class GameCenterAdmin(admin.ModelAdmin):
    list_display = ['id', 'symbol__name', 'game_date', 'start_time', 'end_time',
                    'open_price', 'close_price', 'result', 'create_at']
    list_filter = ['symbol', 'result', 'game_date']
    search_fields = ['symbol__name']
    date_hierarchy = 'game_date'


@admin.register(UserGameSignUp)
class UserGameSignUpAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'game_center__symbol__name',"game_center__game_date", 'point', 'guess',
                    'result', 'is_end', 'create_at', 'end_time']
    list_filter = ['guess', 'result', 'is_end', 'game_center__symbol']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user', 'game_center']


@admin.register(PointRecord)
class PointRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'old_point', 'add_point', 'new_point',
                 'create_at']
    list_filter = [ 'create_at']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']


@admin.register(StudyContent)
class StudyContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'create_at', 'content_preview']
    list_filter = ['status']
    readonly_fields = ['content_preview']

    def content_preview(self, obj):
        return format_html('<div style="max-width: 300px; overflow: hidden;">{}</div>', obj.content[:100])

    content_preview.short_description = '内容'

    def approve(self, request, queryset):
        queryset.update(status=3)
        self.message_user(request, '已审核通过')

    approve.short_description = '审核通过'

    def reject(self, request, queryset):
        queryset.update(status=2)
        self.message_user(request, '已审核不通过')

    reject.short_description = '审核不通过'

    actions = [approve, reject]


@admin.register(StudyGood)
class StudyGoodAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'study_content', 'is_del', 'create_at')
    list_filter = ('is_del', 'create_at')
    search_fields = ('user__username', 'study_content__id')
    ordering = ('-create_at',)


@admin.register(StudyComment)
class StudyCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'study_content', 'short_comment', 'is_del', 'create_at')
    list_filter = ('is_del', 'create_at')
    search_fields = ('user__username', 'comment')
    ordering = ('-create_at',)

    def short_comment(self, obj):
        return obj.comment[:30]
    short_comment.short_description = '评论内容'


@admin.register(StudyCommentGood)
class StudyCommentGoodAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'comment', 'is_del', 'create_at')
    list_filter = ('is_del', 'create_at')
    search_fields = ('user__username', 'comment__id')
    ordering = ('-create_at',)