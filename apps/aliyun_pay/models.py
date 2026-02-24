from django.db import models
import uuid

from django.db import models
from django.conf import settings
from apps.users.models import UserProfile


class AliPaymentOrder(models.Model):
    """支付订单模型"""
    ORDER_STATUS = (
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('failed', '支付失败'),
        ('refunded', '已退款'),
        ('canceled', '已取消'),
    )

    # 订单信息
    orderid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alipay_trade_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="支付宝交易号")

    # 金额信息
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="订单金额")
    subject = models.CharField(max_length=256, verbose_name="订单标题")
    body = models.TextField(blank=True, verbose_name="订单描述")
    usd_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="订单金额(USD)", default=0)

    # 状态和时间
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending', verbose_name="支付状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="支付时间")
    add_vip_time = models.IntegerField(null=True, blank=True, verbose_name="充值会员时长",default=0)
    # 用户信息
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="用户")
    # 赠送积分
    point = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="充值积分赠送", default=0)

    # 回调信息
    notify_time = models.DateTimeField(null=True, blank=True, verbose_name="通知时间")
    notify_data = models.JSONField(default=dict, verbose_name="通知数据")

    class Meta:
        verbose_name = "aliyun"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.orderid} - {self.subject}"
