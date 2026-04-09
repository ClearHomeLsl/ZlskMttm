from django.contrib import admin
from .models import AliPaymentOrder, AliyunPaySymbol


@admin.register(AliPaymentOrder)
class AliPaymentOrderAdmin(admin.ModelAdmin):
    list_display = ['orderid', 'user', 'total_amount', 'subject', 'status', 'created_at', 'paid_at']
    list_filter = ['status', 'created_at']
    search_fields = ['orderid', 'alipay_trade_no', 'user__username']


@admin.register(AliyunPaySymbol)
class AliyunPaySymbolAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_amount', 'point', 'add_vip_time', 'is_del']
    list_filter = ['is_del']
    search_fields = ['name', 'subject']