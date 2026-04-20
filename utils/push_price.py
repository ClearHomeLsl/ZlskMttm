# broadcast_service.py
import os
import sys
import django
import json
project_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MttmView.settings")
django.setup()


from channels.layers import get_channel_layer


async def broadcast_kline_update(symbol, timeframe, r):
    """广播K线更新"""
    channel_layer = get_channel_layer()
    room_name = f"kline_{timeframe}_{symbol}"
    key = f"{timeframe}_{symbol}_price"
    data = r.get(key)
    # 获取当前SAP数据
    sap_data = {
        "m1_xauusd": r.get("m1_XAUUSD_SAR"),
        "m5_xauusd": r.get("m5_XAUUSD_SAR"),
        "m15_xauusd": r.get("m15_XAUUSD_SAR"),
        "m30_xauusd": r.get("m30_XAUUSD_SAR"),
        "h1_xauusd": r.get("h1_XAUUSD_SAR"),
        "h4_xauusd": r.get("h4_XAUUSD_SAR"),
    }
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
                    'sap_data': sap_data,
                    'data': kline_data,
                }
            )
