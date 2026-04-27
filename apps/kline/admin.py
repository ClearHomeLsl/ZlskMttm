from django.contrib import admin
from apps.kline.models import SymbolHistoryPrice

@admin.register(SymbolHistoryPrice)
class SymbolHistoryPriceAdmin(admin.ModelAdmin):
    """用户信息管理（简化版）"""

    list_display = ['symbol', 'open', 'close', 'high', 'low', 'ticket']