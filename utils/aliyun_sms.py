from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util import models as util_models

from MttmView.settings import AccessKeyId, AccessKeySecret


class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client() -> Dysmsapi20170525Client:
        """
        使用AK&SK初始化账号Client
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            access_key_id=AccessKeyId,
            access_key_secret=AccessKeySecret
        )
        # Endpoint 请参考 https://api.aliyun.com/product/Dysmsapi
        config.endpoint = f'dysmsapi.aliyuncs.com'
        return Dysmsapi20170525Client(config)

    @staticmethod
    def send_verify_code(mobile: str, verify_code: str):
        """
        通过手机号和验证码发送短信
        @param mobile: 接收短信的手机号码
        @param verify_code: 发送的验证码
        """
        client = Sample.create_client()

        # 填写您的短信签名和模板ID
        sign_name = '四川智链数科科技'
        template_code = 'SMS_329296008'  # 请替换为您的短信模板ID

        # 创建发送短信的请求对象
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            phone_numbers=mobile,
            sign_name=sign_name,
            template_code=template_code,
            template_param=f'{{"code":"{verify_code}"}}'  # 填写验证码到模板参数
        )

        runtime = util_models.RuntimeOptions()

        # 发送短信请求
        response = client.send_sms_with_options(send_sms_request, runtime)
        # 打印返回结果
        if response.status_code == 200 and response.body and response.body.code == "OK":
            return True, 'ok'
        else:
            return False, response.body.message