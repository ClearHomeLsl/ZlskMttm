from datetime import datetime, timedelta
from alipay import AliPay
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.aliyun_pay.models import  AliPaymentOrder,AliyunPaySymbol
from apps.users.models import UserProfile
from MttmView.settings import *
from utils.user_login_verify import login_verify



# 创建支付宝支付
alipay = AliPay(
    appid=APPID,
    app_notify_url=None,  # 默认回调url
    app_private_key_string=AppPrivateKey,  # 应用私钥文件
    alipay_public_key_string=AlipayPublicKey,  # 支付宝公钥文件
    sign_type="RSA2",  # RSA 或者 RSA2
    debug=True  # 沙箱模式True，正式环境False
)

# Create your views here.
class AliyunPayView(APIView):

    def get(self, request):
        auth_token = request.COOKIES.get('auth_token')
        is_login, jg = login_verify(auth_token)
        if is_login:
            return jg
        symbols = AliyunPaySymbol.objects.filter(is_del=False).order_by("total_amount")
        data = list()
        for symbol in symbols:
            data.append({
                "symbol_id": symbol.id,
                "total_amount": symbol.total_amount,
                "name": symbol.name,
                "subject": symbol.subject,
                "body": symbol.body,
                "point": symbol.point
            })
        return Response({"msg": "ok!", "code": "0", "data": data})


    def post(self, request):
        auth_token = request.COOKIES.get('auth_token')
        is_login, jg = login_verify(auth_token)
        if is_login:
            return jg
        user = jg
        symbol_id = request.data.get('symbol_id')
        try:
            symbol = AliyunPaySymbol.objects.get(id=symbol_id, is_del=False)
        except UserProfile.DoesNotExist:
            return True, Response({"msg": "无效交易产品!", "code": "1003", "response_type": "error"})
        # 保存订单到数据库
        order = AliPaymentOrder.objects.create(
            total_amount=symbol.total_amount,
            subject=symbol.subject,
            body=symbol.body,
            user=user,
            status='pending',
            point=symbol.point,
            add_vip_time=symbol.add_vip_time,
        )

        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=str(order.orderid),  # 商户订单号
            total_amount=str(symbol.total_amount),  # 金额（元）
            subject=symbol.subject,  # 订单标题
            body=symbol.body,
            return_url=ReturnUrl,  # 支付后跳转页面
            notify_url=NotifyUrl  # 支付结果异步通知地址
        )

        pay_url = PayUrl + order_string
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
        if success:
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
        if success:
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
