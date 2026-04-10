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


async def broadcast_kline_update(symbol, timeframe, kline_data):
    """广播K线更新"""
    channel_layer = get_channel_layer()
    room_name = f"kline_{timeframe}_{symbol}"

    await channel_layer.group_send(
        room_name,
        {
            'type': 'kline_update',
            'symbol': symbol,
            'timeframe': timeframe,
            'data': kline_data
        }
    )


async def main():
    """主循环：每秒广播一次"""
    r = get_redis_connect()

    # 配置要广播的数据
    symbols = ['XAUUSD']  # 改成你的交易对
    timeframes = ['m1', 'm5', 'm15', 'm30', 'h1']

    print("开始广播K线数据...")
    print(f"交易对: {symbols}")
    print(f"周期: {timeframes}")
    print("每秒推送一次\n")

    count = 0
    while True:
        start_time = time.time()

        for symbol in symbols:
            for timeframe in timeframes:
                try:
                    # 从Redis获取数据
                    key = f"{timeframe}_{symbol}_price"
                    data = r.get(key)

                    if data:
                        kline_data = json.loads(data)

                        # 更新最新价格
                        now_price = r.get(f"{symbol}_now_price")
                        if now_price and kline_data:
                            kline_data[-1]["close"] = now_price

                        # 广播
                        await broadcast_kline_update(symbol, timeframe, kline_data)
                        print(f"[{count}] ✅ {symbol} {timeframe} - 已广播")

                except Exception as e:
                    print(f"[{count}] ❌ {symbol} {timeframe} - 错误: {e}")

        # 每秒执行一次
        elapsed = time.time() - start_time
        sleep_time = max(0, 0.2 - elapsed)
        await asyncio.sleep(sleep_time)
        count += 1


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n广播服务已停止")