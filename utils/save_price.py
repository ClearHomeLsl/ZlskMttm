import os
import sys
import django
import json
import logging

project_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MttmView.settings")
django.setup()

from apps.kline.models import SymbolHistoryPrice
from utils.DBRedis import get_redis_connect
import pandas as pd
from datetime import datetime,timedelta



def SavePrice(r):
    key = "m1_XAUUSD_price"
    data = r.get(key)
    kline_data  = json.loads(data)
    df = pd.DataFrame(kline_data)
    # print(df)
    # 获取前天时间
    now = datetime.now() - timedelta(days=1)
    today = now.strftime("%Y-%m-%d")

    df = df[df["time"].astype("str").str.contains(today)]
    if df.shape[0] != 0:
        obj_list = list()
        for idx in range(df.shape[0]):
            open = df.iloc[idx]['open']
            high = df.iloc[idx]['high']
            low = df.iloc[idx]['low']
            close = df.iloc[idx]['close']
            time = df.iloc[idx]['time']
            obj_list.append(SymbolHistoryPrice(
                open=open,
                high=high,
                low=low,
                close=close,
                symbol="XAUUSD",
                ticket=time
            ))
        SymbolHistoryPrice.objects.bulk_create(obj_list)
    logging.error(f"执行保存{today} 的数据完毕, 数据量为{df.shape[0]}。")

if __name__ == '__main__':
    r = get_redis_connect()
    SavePrice(r)