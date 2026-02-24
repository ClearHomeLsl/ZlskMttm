from django.shortcuts import render
from rest_framework.views import APIView
from apps.users.models import *
from utils.DBRedis import get_redis_connect
import uuid
from rest_framework.response import Response
from datetime import datetime, timedelta
from MttmView.settings import secure, httponly
from utils.basic_function import get_random_code
from utils.aliyun_sms import Sample


class UserLoginView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not UserProfile.objects.filter(id=user_id).exists():
            return Response({"msg": "用户不存在！", "code": "1003", "response_type": "error"})
        user = UserProfile.objects.get(id=user_id)
        if user.vip_end_time:
            vip_end_time = user.vip_end_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            vip_end_time = ""
        response = Response({
            "msg": "ok!",
            "msg_code": "0",
            "response_type": "success",
            "is_vip": user.is_vip,
            "vip_end_time": vip_end_time,
        })
        return response


    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not UserProfile.objects.filter(username=username).exists():
            return Response({"msg": "用户不存在！", "code": "1003", "response_type": "error"})
        user = UserProfile.objects.get(username=username)
        if not user.check_password(password):
            return Response({"msg": "密码错误", "code": "1001", "response_type": "error"})
        # 登陆成功
        r = get_redis_connect()
        cookie = str(uuid.uuid4()) + "_" + str(user.id) + "_" + user.username
        r.set(username, cookie)
        # 获取用户注册IP
        ip_address = request.META.get('REMOTE_ADDR')
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')  # 如果使用代理，可能需要获取 X-Forwarded-For
        if x_forwarded_for:
            # 如果经过多个代理，X-Forwarded-For 会有多个值，第一个是真实 IP
            ip_address = x_forwarded_for.split(',')[0].strip()
        user.last_login_ip = ip_address
        # 北京时间
        user.last_login_time = datetime.now() + timedelta(hours=8)
        user.save()
        # 配置返回内容
        response = Response({
            "msg": "登陆成功!",
            "msg_code": "0",
            "response_type": "success",
            "is_vip": user.is_vip,
            "vip_end_time": user.vip_end_time,
        })
        # 设置认证 Token Cookie
        response.set_cookie(
            key='auth_token',
            value=cookie,
            max_age=3600 * 24 * 7,  # 7天
            httponly=httponly,          # 防止 XSS
            secure=secure,            # 仅 HTTPS（生产环境）
            samesite='Lax'
        )
        print("response:", response)
        return response


class UserRegisterView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        mobile = request.data.get('mobile')
        username = request.data.get('username')
        password = request.data.get('password')
        verify_code = request.data.get('verify_code')
        print(mobile , username , password)
        if not (mobile and username and password):
            return Response({"msg": "缺少指定参数", "code": "1002", "response_type": "error"})
        # 验证验证码是否正确
        if not verify_code:
            return Response({"msg": "未输入验证码！", "code": "1002", "response_type": "error"})
        r = get_redis_connect()
        user_verify_str = f"zlsk_login_{mobile}"
        sys_verify_code = r.get(user_verify_str)  # 失效时间300秒，也就是5分钟
        if str(sys_verify_code) != str(verify_code):
            return Response({"msg": "验证码错误！", "code": "1002", "response_type": "error"})
        # 获取用户注册IP
        ip_address = request.META.get('REMOTE_ADDR')
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')  # 如果使用代理，可能需要获取 X-Forwarded-For
        if x_forwarded_for:
            # 如果经过多个代理，X-Forwarded-For 会有多个值，第一个是真实 IP
            ip_address = x_forwarded_for.split(',')[0].strip()
        user = UserProfile.objects.create(
            username=username,
            mobile=mobile,
            password=password,
            register_ip=ip_address,
        )
        # 创建用户后整理登陆信息，实现自动登陆
        r = get_redis_connect()
        cookie = str(uuid.uuid4()) + "_" + str(user.id) + "_" + user.username
        r.set(username, cookie)

        response = Response({"msg": "注册成功!", "msg_code": "0", "response_type": "success"})
        # 设置认证 Token Cookie
        response.set_cookie(
            key='auth_token',
            value=cookie,
            max_age=3600 * 24 * 7,  # 7天
            httponly=httponly,          # 防止 XSS
            secure=secure,            # 仅 HTTPS（生产环境）
            samesite='Lax'
        )
        return response


class V2GetVerifyCode(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        mobile = request.data.get("mobile")
        # 判断是否为国内手机号
        if mobile[0] != "1" or len(mobile) != 11:
            return Response({"msg": "手机号格式错误！", "code": "1005", "response_type": "error"})
        try:
            int(mobile)
        except TypeError:
            return Response({"msg": "手机号格式错误！", "code": "1005", "response_type": "error"})
        # 生成6位数随机验证码
        verify_code = get_random_code()
        is_send, msg = Sample.send_verify_code(mobile, verify_code)
        if is_send:
            # 发送成功，保存redis
            r = get_redis_connect()
            user_verify_str = f"zlsk_login_{mobile}"
            r.set(user_verify_str, verify_code, ex="300")  # 失效时间300秒，也就是5分钟
            return Response({"msg": "ok", "msg_code": "0"})
        else:
            # 发送失败，返回错误信息
            if msg == "触发小时级流控Permits:5":
                msg = "验证码已达到发送上限，请一小时后尝试."
            return Response({"msg": msg, "msg_code": "200001"})

