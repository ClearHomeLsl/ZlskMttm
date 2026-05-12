from urllib import request

from django.shortcuts import render
from rest_framework.views import APIView
from apps.users.models import *
from utils.DBRedis import get_redis_connect
import uuid
import os
from rest_framework.response import Response
from datetime import datetime, timedelta
from MttmView.settings import secure, httponly
from utils.basic_function import get_random_code
from utils.aliyun_sms import Sample
from django.db.models import Q
from utils.user_login_verify import login_verify
from decimal import Decimal
from django.db import transaction
from django_ckeditor_5.forms import UploadFileForm
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from MttmView.settings import study_file_path, SalesContactInformationData
from apps.users.utils import get_page_size



class UserLoginView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        # 从 cookie 获取用户信息
        auth_token = request.COOKIES.get('auth_token')
        is_login, jg = login_verify(auth_token)
        if is_login:
            return jg
        user = jg
        if user.vip_end_time:
            vip_end_time = user.vip_end_time.strftime("%Y-%m-%d %H:%M:%S")
            # 判断会员是否过期
            now = datetime.now()
            if user.vip_end_time < now:
                # 会员已过期
                user.vip_end_time = None
                user.is_vip = False
                user.save()
                vip_end_time = ""
        else:
            vip_end_time = ""

        response = Response({
            "msg": "ok!",
            "msg_code": "0",
            "response_type": "success",
            "is_vip": user.is_vip,
            "vip_end_time": vip_end_time,
            "is_vip_experience": user.is_vip_experience,
            "is_receive_vip": user.is_receive_vip,
            "point": user.point,
            "point_level": user.point_level,
            "username": user.username,
            "email" : user.email,
            "user_stutas": user.user_stutas,
            "user_id": user.id,
            "is_first": user.is_first_pay,
            "is_active": user.is_active,
        })
        return response


    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        # print(request.data)
        if not UserProfile.objects.filter(Q(username=username)|Q(mobile=username)).exists():
            return Response({"msg": "用户不存在！", "code": "1003", "response_type": "error"})
        user = UserProfile.objects.get(Q(username=username)|Q(mobile=username))
        if not user.check_password(password):
            return Response({"msg": "密码错误", "code": "1001", "response_type": "error"})
        # 登陆成功
        r = get_redis_connect()
        cookie = str(uuid.uuid4()) + "_" + str(user.id) + "_" + user.mobile
        r.set(user.mobile, cookie)
        # 获取用户注册IP
        ip_address = request.META.get('REMOTE_ADDR')
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')  # 如果使用代理，可能需要获取 X-Forwarded-For
        if x_forwarded_for:
            # 如果经过多个代理，X-Forwarded-For 会有多个值，第一个是真实 IP
            ip_address = x_forwarded_for.split(',')[0].strip()
        user.last_login_ip = ip_address
        # 北京时间
        user.last_login_time = datetime.now()
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
        return response


class UserRegisterView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        mobile = request.data.get('mobile')
        username = request.data.get('username')
        password = request.data.get('password')
        verify_code = request.data.get('verify_code')
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
        if UserProfile.objects.filter(Q(username=username)|Q(mobile=mobile)).exists():
            return Response({"msg": "手机号或用户名已注册", "code": "1003", "response_type": "error"})
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
            point=1000
        )
        # 注册赠送积分
        PointRecord.objects.create(
            user=user,
            old_point=0,
            add_point=1000,
            new_point=1000,
            change_oper=4
        )
        # 创建用户后整理登陆信息，实现自动登陆
        r = get_redis_connect()
        cookie = str(uuid.uuid4()) + "_" + str(user.id) + "_" + user.mobile
        r.set(mobile, cookie)

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
        print(mobile, verify_code)
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


class ReceiveVipView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        # 从 cookie 获取用户信息
        auth_token = request.COOKIES.get('auth_token')
        is_login, jg = login_verify(auth_token)
        if is_login:
            return jg
        user = jg
        if user.is_receive_vip:
            return Response({"msg": "已领取过会员，无法重新领取", "code": "2001", "response_type": "error"})
        user.is_receive_vip = True
        user.is_vip_experience = True
        user.is_vip = True
        user.vip_end_time = datetime.now() + timedelta(days=1)
        user.save()
        return Response({"msg": "ok", "msg_code": "0"})


class GameCenterView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        # 从 cookie 获取用户信息
        auth_token = request.COOKIES.get('auth_token')
        is_login, jg = login_verify(auth_token)
        if is_login:
            return jg
        now = datetime.now()
        user = jg
        # 创建redis对象
        r = get_redis_connect()
        # 获取当前可参赛的竞猜
        games = GameCenter.objects.filter(start_time__lte=now, game_date__gte=now)
        ing_game_data = []
        for game in games:
            now_price = r.get(f"{game.symbol.name}_now_price")
            data = {
                "game_id": game.id,
                "Deadline": game.game_date,
                "nick_name": game.symbol.nick_name,
                "symbol": game.symbol.name,
                "end_time": game.end_time,
                "now_price": now_price if now_price else "0.00"
            }
            ing_game_data.append(data)
        # 获取已参与的竞猜
        signups = UserGameSignUp.objects.filter(user=user)
        result_dict = {1: "win(赢)", 2: "lose(输)"}
        sign_history = list()
        for signup in signups:
            data = {
                "sign_id": signup.id,
                "name": signup.game_center.game_date.strftime("%Y-%m-%d") + "竞猜",
                "opertion": signup.guess,
                "is_end": signup.is_end,
                "result": result_dict.get(signup.result) if signup.is_end else "待开奖",
            }
            sign_history.append(data)
        return Response({"msg": "ok", "msg_code": "0", "ing_game_data": ing_game_data, "sign_history": sign_history})

    @transaction.atomic
    def post(self, request):
        auth_token = request.COOKIES.get('auth_token')
        is_login, jg = login_verify(auth_token)
        if is_login:
            return jg
        guess = request.data.get('guess')
        game_id = request.data.get('game_id')
        point = request.data.get('point')
        try:
            point = int(point)
        except ValueError:
            return Response({"msg": "参数异常!", "code": "1001",})
        user = jg
        if UserGameSignUp.objects.filter(game_center__id=game_id, user_id=user.id).exists():
            return Response({"msg": "该竞猜已报名，请勿重复报名。", "code": "2001",})
        if user.point < point:
            return Response({"msg": "积分不足！", "code": "2002", })

        UserGameSignUp.objects.create(
            user=user,
            game_center=GameCenter.objects.get(id=game_id),
            point=Decimal(str(point)),
            guess=guess,
        )
        # 减少积分
        PointRecord.objects.create(
            user=user,
            old_point=user.point,
            add_point=-point,
            new_point=(user.point - point),
            change_oper=1,
        )
        user.point -= point
        user.save()
        return Response({"msg": "竞猜成功", "msg_code": "0"})



class ImageUploadAPIView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_file = request.FILES["file"]
            # 生成唯一文件名
            ext = uploaded_file.name.split('.')[-1]
            filename = f"{uuid.uuid4().hex}.{ext}"
            # 指定保存路径（相对于 MEDIA_ROOT）
            upload_path = os.path.join('media/images/study/', filename)
            # 保存文件
            saved_path = default_storage.save(upload_path, ContentFile(uploaded_file.read()))
            # 构建可访问的URL
            url = default_storage.url(saved_path)
            return Response({"url": study_file_path+url})
        return Response({"msg": "图片上传异常！", "code": "2001" })


class StudyContentView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        auth_token = request.COOKIES.get('auth_token')
        is_login, jg = login_verify(auth_token)
        if is_login:
            return jg
        user = jg
        result = []
        # 获取当前所有人审核通过的文章
        ok_data = StudyContent.objects.filter(status=3)
        for ok_d in ok_data:
            result.append({
                "id": ok_d.id,
                "title": ok_d.title,
                "content": ok_d.content,
                "user": ok_d.user.username,
                "create_time": ok_d.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                "cover_image_path": ok_d.cover_image_path,
                "status": ok_d.status,
                "good_count": StudyGood.objects.filter(study_content=ok_d, is_del=False).count(),
                "comment_count": StudyComment.objects.filter(study_content=ok_d, is_del=False).count(),
                "is_my": ok_d.user.id == user.id,

            })
        # 获取当前还在审核中的文章
        ing_data = StudyContent.objects.filter(status__in=[1,2], user=user)
        for ing_d in ing_data:
            result.append({
                "id": ing_d.id,
                "title": ing_d.title,
                "content": ing_d.content,
                "user": ing_d.user.username,
                "create_time": ing_d.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                "cover_image_path": ing_d.cover_image_path,
                "status": ing_d.status,
                "good_count": 0,
                "comment_count": 0,
                "is_my": True,
            })
        # print(result)
        return Response({"msg": "ok", "msg_code": "0", "data": result})

    def post(self, request):
        auth_token = request.COOKIES.get('auth_token')
        is_login, jg = login_verify(auth_token)
        if is_login:
            return jg
        user = jg
        title = request.data.get('title')
        content = request.data.get('content')
        cover_image_path = request.data.get('cover_image_path', "")
        if StudyContent.objects.filter(title=title, content=content, user=user).exists():
            return Response({"msg": "文章内容标题重复，请勿重复请求！", "code": "2001",})
        # cover_image_path = content
        StudyContent.objects.create(
            title=title,
            content=content,
            user=user,
            cover_image_path=cover_image_path,
        )
        return Response({"msg": "ok", "msg_code": "0"})


class StudyContentDetailView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request, content_id):
        auth_token = request.COOKIES.get('auth_token')
        is_login, jg = login_verify(auth_token)
        if is_login:
            return jg
        user = jg
        study_content = StudyContent.objects.get(id=content_id)
        goods = StudyGood.objects.filter(study_content=study_content, is_del=False)
        good_count = goods.count()
        good_ids = goods.values_list("user__id", flat=True)
        comments = StudyComment.objects.filter(study_content=study_content, is_del=False)
        comments_detail = []
        for comment in comments:
            comments_good = StudyCommentGood.objects.filter(comment=comment, is_del=False)
            comments_detail.append({
                "id": comment.id,
                "create_time": comment.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                "comment": comment.comment,
                "good_count": comments_good.count(),
                "good_ids": comments_good.values_list("user__id", flat=True),
                "username": "Zlsk用户"+ comment.user.username,
            })
        data = {
            "id": study_content.id,
            "title": study_content.title,
            "content": study_content.content,
            "comments_detail": comments_detail,
            "create_time": study_content.create_at.strftime("%Y-%m-%d %H:%M:%S"),
            "user": study_content.user.username,
            "good_count": good_count,
            "good_id": good_ids,
            "is_my": study_content.user.id == user.id,

        }
        print(data)
        return Response({"msg": "ok", "msg_code": "0", "data": data})

    def post(self, request, content_id):
        auth_token = request.COOKIES.get('auth_token')
        is_login, jg = login_verify(auth_token)
        if is_login:
            return jg
        user = jg
        oper_type = request.data.get('oper_type')
        if oper_type == "good":
            is_good = request.data.get('is_good')
            if StudyGood.objects.filter(study_content__id=content_id, user=user).exists():
                good_oper = StudyGood.objects.get(study_content__id=content_id, user=user)
                if good_oper.is_del != is_good:
                    good_oper.is_del = is_good
                    good_oper.save()
            else:
                content = StudyContent.objects.get(id=content_id)
                StudyGood.objects.create(study_content=content, user=user, is_del=is_good)
            return Response({"msg": "ok", "code": "0"})
        elif oper_type == "comment":
            comment = request.data.get('comment')
            if not StudyComment.objects.filter(study_content__id=content_id, user=user, comment=comment).exists():
                content = StudyContent.objects.get(id=content_id)
                StudyComment.objects.create(study_content=content, user=user, comment=comment)
            return Response({"msg": "ok", "code": "0"})
        else:
            return Response({"msg": "参数异常！", "code": "1001"})


class CommentOperGoodView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        auth_token = request.COOKIES.get('auth_token')
        is_login, jg = login_verify(auth_token)
        if is_login:
            return jg
        user = jg
        comment_id = request.data.get('comment_id')
        is_good = request.data.get('is_good')
        if not comment_id and (is_good in [True, False]):
            return Response({"msg": "参数异常", "code": "0"})
        if StudyCommentGood.objects.filter(comment__id=comment_id, user=user).exists():
            good_oper = StudyCommentGood.objects.get(comment__id=comment_id, user=user)
            if good_oper.is_del != is_good:
                good_oper.is_del = is_good
                good_oper.save()
        else:
            comment = StudyComment.objects.get(id=comment_id)
            StudyCommentGood.objects.create(comment=comment, user=user, is_del=is_good)
        return Response({"msg": "ok", "code": "0"})


class MessageRecordView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        email = request.data.get('email')
        if EmailSub.objects.filter(email=email).exists():
            return Response({"msg": f"邮箱{email}已订阅，无法重复订阅! ", "msg_code": "2001"})
        EmailSub.objects.create(email=email)
        return Response({"msg": "ok", "code": "0"})


class AgencyApplicationView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        name = request.data.get('name')
        mobile = request.data.get('mobile')
        email = request.data.get('email')
        content = request.data.get('content')
        if AgencyApplication.objects.filter(name=name, mobile=mobile,
                                            email=email, content=content, is_connect=False).exists():
            return Response({"msg": f"该申请已有,请勿重复申请!  ", "msg_code": "2001"})
        AgencyApplication.objects.create(name=name, mobile=mobile,email=email, content=content)
        return Response({"msg": "ok", "code": "0"})


class UserChangeView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        auth_token = request.COOKIES.get('auth_token')
        is_login, jg = login_verify(auth_token)
        if is_login:
            return jg
        user = jg
        user.email = request.data.get('email')
        user.save()
        return Response({"msg": "ok", "code": "0", "email": user.email})


class SalesContactInformationView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        data = {
            "content" : SalesContactInformationData
        }
        return Response({"msg": "ok", "code": "0", "data": data})


class ActingManageView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        auth_token = request.COOKIES.get('auth_token')
        is_login, jg = login_verify(auth_token)
        if is_login:
            return jg
        user = jg
        if not user.is_active:
            return Response({"msg": f"该用户无代理权限，无法获取代理数据。", "msg_code": "1001"})
        active_wallet = UserActiveWallet.objects.get(user=user)

        # 查询代理获利记录 获取分页参数
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 20)  # 默认每页20条
        model_obj = UserActiveWalletLog.objects.filter(relationship__active=user)
        page, page_size, data, total_pages = get_page_size(page, page_size, model_obj)

        user_wallet_detail = {
            "active_code": user.active_code,
            "balance": active_wallet.balance,
            "freeze": active_wallet.freeze,
        }
        active_wallet_log = list()
        for d in data:
            active_wallet_log.append({
                "amount": d.amount,
                "thaw_time": d.thaw_time,
                "is_thaw": d.is_thaw,
                "client": d.relationship.client.username
            })
        pagination = {
                "current_page": page,
                "page_size": page_size,
                "total_count": model_obj.count(),
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
        }
        response = Response({
            "msg": "ok",
            "code": "0",
            "user_wallet_detail": user_wallet_detail,
            "active_wallet_log": active_wallet_log,
            "pagination": pagination,
        })
        return response