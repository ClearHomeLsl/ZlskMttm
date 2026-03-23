

from rest_framework.views import APIView
from apps.users.models import *
from rest_framework.response import Response
from apps.news.models import FinanceNews
from utils.DBRedis import get_redis_connect


class NewsListView(APIView):
    def get(self, request):
        user_id = request.user.id
        if not user_id:
            return Response({"msg": "用户不存在!", "msg_code": "1003"})
        if not UserProfile.objects.filter(id=user_id).exists():
            return Response({"msg": "用户不存在!", "msg_code": "1003"})
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