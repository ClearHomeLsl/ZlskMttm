from django.db import models
import uuid
# Create your models here.

class SymbolHistoryPrice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.CharField(verbose_name='产品名称', max_length=255, null=False, blank=False)
    open = models.DecimalField(verbose_name='开盘价', max_digits=10, decimal_places=4, null=False, blank=False)
    close = models.DecimalField(verbose_name='收盘价', max_digits=10, decimal_places=4, null=False, blank=False)
    high = models.DecimalField(verbose_name='最高价', max_digits=10, decimal_places=4, null=False, blank=False)
    low = models.DecimalField(verbose_name='最低价', max_digits=10, decimal_places=4, null=False, blank=False)
    ticket = models.DateTimeField(verbose_name='时间', null=False, blank=False)

    class Meta:
        verbose_name = "产品历史价格"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.symbol + self.ticket.strftime('%Y-%m-%d %H:%M')