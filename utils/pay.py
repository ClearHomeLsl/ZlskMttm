import os
from datetime import datetime
from alipay import AliPay
from django.conf import settings
from django.utils import timezone

class AlipayPayment:
    def __init__(self):
        self.app_id = settings.ALIPAY_CONFIG['app_id']
        self.app_notify_url = settings.ALIPAY_CONFIG['notify_url']
        self.return_url = settings.ALIPAY_CONFIG['return_url']
        self.debug = settings.ALIPAY_CONFIG['debug']
        self.sign_type = settings.ALIPAY_CONFIG['sign_type']

        # 读取密钥文件
        app_private_key_path = settings.ALIPAY_CONFIG['app_private_key_path']
        alipay_public_key_path = settings.ALIPAY_CONFIG['alipay_public_key_path']

        # 读取密钥内容
        with open(app_private_key_path, 'r') as f:
            app_private_key = f.read()

        with open(alipay_public_key_path, 'r') as f:
            alipay_public_key = f.read()

        # 清理密钥格式
        app_private_key = self._clean_private_key(app_private_key)
        alipay_public_key = self._clean_public_key(alipay_public_key)
        print(alipay_public_key)
        print("====" * 30)
        print(app_private_key)
        # 初始化支付宝支付对象
        self.alipay = AliPay(
            appid=self.app_id,
            app_notify_url=self.app_notify_url,
            app_private_key_string=app_private_key,
            alipay_public_key_string=alipay_public_key,
            sign_type=self.sign_type,
            debug=self.debug  # 沙箱环境
        )

    def create_payment(self, order_id, total_amount, subject, body=None):
        """
        创建支付订单
        """
        # 生成支付链接
        order_string = self.alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(total_amount),
            subject=subject,
            body=body or '',
            return_url=self.return_url,
            notify_url=self.app_notify_url  # 可选，不填则使用默认notify url
        )

        # 根据环境生成支付URL
        if self.debug:
            base_url = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'
        else:
            base_url = "https://openapi.alipay.com/gateway.do"

        payment_url = f"{base_url}?{order_string}"
        return payment_url

    def _clean_private_key(self, key_string):
        """清理私钥格式"""
        key_string = key_string.strip()

        # 处理不同格式的私钥
        if '-----BEGIN RSA PRIVATE KEY-----' not in key_string:
            # 如果是单行格式，添加标记
            lines = key_string.split('\n')
            if len(lines) == 1:
                # 格式化密钥
                formatted_key = ""
                for i in range(0, len(key_string), 64):
                    formatted_key += key_string[i:i + 64] + "\n"
                key_string = f"-----BEGIN RSA PRIVATE KEY-----\n{formatted_key}-----END RSA PRIVATE KEY-----"

        return key_string

    def _clean_public_key(self, key_string):
        """清理公钥格式"""
        key_string = key_string.strip()

        if '-----BEGIN PUBLIC KEY-----' not in key_string:
            # 确保公钥格式正确
            lines = key_string.split('\n')
            if len(lines) == 1 and len(key_string) > 200:
                formatted_key = ""
                for i in range(0, len(key_string), 64):
                    formatted_key += key_string[i:i + 64] + "\n"
                key_string = f"-----BEGIN PUBLIC KEY-----\n{formatted_key}-----END PUBLIC KEY-----"

        return key_string

    def verify_payment(self, data):
        """
        验证支付结果
        """
        # 移除sign_type参数（阿里建议）
        if 'sign_type' in data:
            data.pop('sign_type')
        sign = data.get("sign")
        # 验证签名
        success = self.alipay.verify(data, sign)
        return success

    def query_payment(self, order_id):
        """
        查询订单状态
        """
        try:
            result = self.alipay.api_alipay_trade_query(out_trade_no=order_id)
            return result
        except Exception as e:
            print(f"查询订单失败: {e}")
            return None