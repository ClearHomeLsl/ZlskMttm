from redis_connect import *
import json
from datetime import datetime
import time



def psar_trend(data, step=0.02, max_step=0.2):
    """
    data: list of dicts, each like:
    {
        "time": "2025-12-03 00:01:00",
        "open": 4206.28,
        "high": 4207.27,
        "low": 4205.96,
        "close": 4207.03
    }
    """
    # 初始化
    psar = data[0]["low"]
    bull = True               # 初始趋势为上涨
    af = step
    ep = data[0]["high"]      # 极值点

    # 遍历 K 线
    for i in range(1, len(data)):
        prev = data[i - 1]
        curr = data[i]

        # 计算新的SAR
        psar = psar + af * (ep - psar)

        if bull:  # 上涨趋势
            if psar > curr["low"]:
                # 反转 → 变成下跌
                bull = False
                psar = ep     # psar跳到前一次极值点
                ep = curr["low"]
                af = step
            else:
                if curr["high"] > ep:
                    ep = curr["high"]
                    af = min(af + step, max_step)

        else:  # 下跌趋势
            if psar < curr["high"]:
                # 反转 → 变成上涨
                bull = True
                psar = ep
                ep = curr["high"]
                af = step
            else:
                if curr["low"] < ep:
                    ep = curr["low"]
                    af = min(af + step, max_step)

    # 返回最终趋势
    return "up" if bull else "down"


if __name__ == '__main__':
    r = get_redis_connect()
    old_jg = None
    while 1:
        data = r.get(f"m1_XAUUSD_price")
        data = json.loads(data)
        jg = psar_trend(data)
        if old_jg:
            if old_jg != jg:
                now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                content = f"北京时间: {now_datetime}， 趋势发生反转为: 由{old_jg}更变为{jg}, 价格为: {round(data[-1]['close'], 1)}!"
                print(content)
                old_jg = jg
                need_msg = {
                    "content": content,
                    "title": "趋势变动",
                    "datetime": now_datetime
                }
                r.rpush("m1_trend_change", json.dumps(need_msg))
        else:
            print(f"北京时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}， 首次执行，当前趋势为: {jg}!")
            old_jg = jg
        time.sleep(1)