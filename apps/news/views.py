from rest_framework.views import APIView
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

        # 获取分页参数
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 20)  # 默认每页20条

        try:
            page = int(page)
            page_size = int(page_size)
            # 限制最大每页数量，防止恶意请求
            page_size = min(page_size, 100)
        except ValueError:
            page = 1
            page_size = 20

        # 计算起始和结束位置
        start = (page - 1) * page_size
        end = start + page_size

        # 获取总记录数
        total_count = FinanceNews.objects.count()

        # 分页查询
        news = FinanceNews.objects.order_by("-release_time")[start:end]

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

        # 计算总页数
        total_pages = (total_count + page_size - 1) // page_size

        response = Response({
            "msg": "ok!",
            "msg_code": "0",
            "response_type": "success",
            "data": datas,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            },
            "before_last_up_time": before_last_up_time
        })
        return response