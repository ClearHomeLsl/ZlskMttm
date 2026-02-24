import json
import pandas as pd

from django.shortcuts import render
from rest_framework.views import APIView
from apps.users.models import *
from utils.DBRedis import get_redis_connect
import uuid
from rest_framework.response import Response
from datetime import datetime, timedelta


class KlineIndexView(APIView):
    def get(self, request):
        return render(request, template_name="index.html")


class KlineCandlestickDataView(APIView):
    def get(self, request):
        cookie = request.COOKIES.get('auth_token')
        if not cookie:
            return Response({"msg": "用户未登陆或在其他地方登陆，请重新登陆！", "code": "1003", "response_type": "error"})
        r = get_redis_connect()
        _, user_id, username = cookie.split('_')
        if not r.get(username):
            return Response({"msg": "用户未登陆或在其他地方登陆，请重新登陆！", "code": "1003", "response_type": "error"})
        timeframe = request.query_params.get('timeframe', '1m')
        symbol = request.query_params.get('symbol')
        if timeframe and symbol:
            r = get_redis_connect()
            data = r.get(f"{timeframe}_{symbol}_price")
            data = json.loads(data)
            now_price = r.get(f"{symbol}_now_price")
            data[-1]["close"] = now_price
            return Response({"msg": "ok!", "code": "0", "response_type": "success", "data": data})
        else:
            return Response({"msg": "参数异常!", "code": "1004", "response_type": "error"})


class KlineOldPriceView(APIView):
    def get(self, request):
        cookie = request.COOKIES.get('auth_token')
        if not cookie:
            return Response({"msg": "用户未登陆或在其他地方登陆，请重新登陆！", "code": "1003", "response_type": "error"})
        r = get_redis_connect()
        _, user_id, username = cookie.split('_')
        if not r.get(username):
            return Response({"msg": "用户未登陆或在其他地方登陆，请重新登陆！", "code": "1003", "response_type": "error"})
        symbol = request.query_params.get('symbol')
        if symbol:
            r = get_redis_connect()
            data = r.get(f"h1_{symbol}_price")
            data = json.loads(data)
            df = pd.DataFrame(data)
            df["date"] = df["time"].astype("str").str[:10]
            old_price = df.groupby("date").last().iloc[-2]["close"].astype("str")
            return Response({"msg": "ok!", "code": "0", "response_type": "success", "old_price": old_price})
        else:
            return Response({"msg": "参数异常!", "code": "1004", "response_type": "error"})


class KlineNotificationsView(APIView):
    def get(self, request):
        cookie = request.COOKIES.get('auth_token')
        if not cookie:
            return Response({"msg": "用户未登陆或在其他地方登陆，请重新登陆！", "code": "1003", "response_type": "error"})
        r = get_redis_connect()
        _, user_id, username = cookie.split('_')
        if not r.get(username):
            return Response({"msg": "用户未登陆或在其他地方登陆，请重新登陆！", "code": "1003", "response_type": "error"})
        timeframe = request.query_params.get('timeframe', '1m')
        symbol = request.query_params.get('symbol')
        if timeframe and symbol:
            r = get_redis_connect()
            trend_change = r.lrange(f'{timeframe}_trend_change', 0, -1)
            trend_change = trend_change[-20:]
            trend_change = [json.loads(d) for d in trend_change]
            return Response({"msg": "ok!", "code": "0", "response_type": "success", "data": trend_change})
        else:
            return Response({"msg": "参数异常!", "code": "1004", "response_type": "error"})
