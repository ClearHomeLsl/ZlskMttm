from datetime import datetime, timedelta
from alipay import AliPay
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.aliyun_pay.models import  AliPaymentOrder
from apps.users.models import UserProfile
from decimal import Decimal
from utils.pay import AlipayPayment
from MttmView.settings import *



# 创建支付宝支付
alipay = AliPay(
    appid=ALIPAY_CONFIG['app_id'],
    app_notify_url=None,  # 默认回调url
    app_private_key_string=ALIPAY_CONFIG['app_private_key'],  # 应用私钥文件
    alipay_public_key_string=ALIPAY_CONFIG['alipay_public_key'],  # 支付宝公钥文件
    sign_type="RSA2",  # RSA 或者 RSA2
    debug=False  # 沙箱模式True，正式环境False
)

# Create your views here.
class AliyunPayView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        trade_type = request.data.get('type')
        amount = request.data.get('amount')
        points = request.data.get('points')
        user = UserProfile.objects.get(id=user_id)
        subject = "四川智链数科VIP充值"
        if trade_type == "day":
            body = "VIP日卡"
            add_vip_time = 1
        elif trade_type == "week":
            body = "VIP周卡"
            add_vip_time = 7
        elif trade_type == "month":
            body = "VIP月卡"
            add_vip_time = 30
        elif trade_type == "three_month":
            body = "VIP季卡"
            add_vip_time = 90
        elif trade_type == "half":
            body = "VIP半年卡"
            add_vip_time = 180
        elif trade_type == "year":
            body = "VIP年卡"
            add_vip_time = 365
        else:
            return Response({"msg": "参数异常！", "msg_code": "300001"})
        # 获取充值金额，并换汇
        total_amount = round(Decimal(amount) * Decimal(7.1), 2)
        print(total_amount , subject, body)
        # 保存订单到数据库
        order = AliPaymentOrder.objects.create(
            total_amount=total_amount,
            subject=subject,
            body=body,
            user=user,
            status='pending',
            point=Decimal(points),
            add_vip_time=add_vip_time
        )

        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=str(order.orderid),  # 商户订单号
            total_amount=str(total_amount),  # 金额（元）
            subject="subject",  # 订单标题
            body=body,
            return_url=ALIPAY_CONFIG["return_url"],  # 支付后跳转页面
            notify_url=ALIPAY_CONFIG["notify_url"]  # 支付结果异步通知地址
        )

        pay_url = "https://openapi-sandbox.dl.alipaydev.com/gateway.do?" + order_string
        print(pay_url)
        # 重定向到支付宝支付页面
        return Response({"msg": "ok!", "code": "0", "response_type": "success", "pay_url": pay_url})


class AliyunPayCallBackView(APIView):
    def post(self, request):
        print(request.data)
        return

class AliPayNotifyView(APIView):
    def post(self, request):
        data = request.POST.dict()
        success = alipay.verify(data, data.get("sign"))
        if data.get("sign", False):
            # 处理支付成功的逻辑
            out_trade_no = data.get('out_trade_no')  # 商户订单号
            # trade_no = data.get('trade_no')  # 支付宝交易号

            order = AliPaymentOrder.objects.get(orderid=out_trade_no)
            order.status = 'paid'
            order.paid_at = datetime.now()
            user = order.user
            if user.is_vip:
                # 延长会员到期时间
                user.vip_end_time += timedelta(days=order.add_vip_time)
            else:
                # 成为会员，并设置会员到期时间
                user.is_vip = True
                user.vip_end_time = datetime.now() + timedelta(days=order.add_vip_time)
            user.save()
            order.save()
            return Response()
        else:
            print("签名验证失败！")
            return Response({"msg": "error!", "code": "300002", "response_type": "feiad"})

class AliPayMentResultView(APIView):
    def get(self, request):
        data = request.GET.dict()
        print(data)
        success = alipay.verify(data, data.get("sign"))
        if data.get("sign", False):
            # 支付成功
            order_info = {
                'order_no': data.get('out_trade_no', 'TEST001'),
                'alipay_no': data.get('trade_no', '202401092200140001'),
                'amount': data.get('total_amount', '0.01'),
                'subject': data.get('subject', 'VIP充值'),
                'pay_time': data.get('gmt_payment', '2024-01-09 10:00:00'),
            }
            return render(request, 'payment_success.html', {'order': order_info})
        else:
            # 支付失败
            error_info = {
                'order_no': data.get('out_trade_no', 'TEST001'),
                'error_msg': data.get('sub_msg', '支付失败'),
                'amount': data.get('total_amount', '0.01'),
            }
            return render(request, 'failure.html', {'error': error_info})
