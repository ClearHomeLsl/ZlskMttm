

from rest_framework.views import APIView
from apps.users.models import *
from rest_framework.response import Response
from apps.news.models import FinanceNews
from utils.DBRedis import get_redis_connect
from utils.user_login_verify import login_verify


class NewsListView(APIView):
    permission_classes = ()
    authentication_classes = ()
    def get(self, request):
        # 从 cookie 获取用户信息
        auth_token = request.COOKIES.get('auth_token')
        is_login, jg = login_verify(auth_token)
        if is_login:
            return jg
        news = FinanceNews.objects.order_by("-release_time")[:10]
        datas = list()
        for new in news:
            datas.append({
                "id": new.id,
                "title": new.title,
                "content": new.content,
                "author": new.author,
                "news_link": new.news_link,
                "release_time": new.release_time,
                "source": "jin10"
            })
        r = get_redis_connect()
        before_last_up_time = r.get("before_last_up_time")
        response = Response({
            "msg": "ok!",
            "msg_code": "0",
            "response_type": "success",
            "data": datas,
            "before_last_up_time": before_last_up_time
        })
        return response