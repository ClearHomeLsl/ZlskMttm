# broadcast_service.py
import os
import sys
import django
import json
import asyncio
import time

project_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MttmView.settings")
django.setup()


from channels.layers import get_channel_layer
from utils.DBRedis import get_redis_connect


async def broadcast_kline_update(symbol, timeframe, r):
    """广播K线更新"""
    channel_layer = get_channel_layer()
    room_name = f"kline_{timeframe}_{symbol}"
    key = f"{timeframe}_{symbol}_price"
    data = r.get(key)
    if data:
        kline_data = json.loads(data)
        # 更新最新价格
        now_price = r.get(f"{symbol}_now_price")
        if now_price and kline_data:
            kline_data[-1]["close"] = now_price
            await channel_layer.group_send(
                room_name,
                {
                    'type': 'kline_update',
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'data': kline_data
                }
            )
