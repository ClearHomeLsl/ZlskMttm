import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import pytz
from decimal import Decimal


# 初始化MT5连接
if not mt5.initialize():
    print("MT5初始化失败，错误代码:", mt5.last_error())
    quit()


class GetSymbolPrice(object):
    def __init__(self, run_type, symbol="XAUUSD"):
        if run_type == "m1":
            # 一分钟时间周期预算
            self.timeframe = mt5.TIMEFRAME_M1
            min_num = 1
        elif run_type == "m5":
            # 五分钟时间周期预算
            self.timeframe = mt5.TIMEFRAME_M5
            min_num = 5
        elif run_type == "m15":
            # 十五分钟时间周期预算
            self.timeframe = mt5.TIMEFRAME_M15
            min_num = 15
        elif run_type == "m30":
            # 十五分钟时间周期预算
            self.timeframe = mt5.TIMEFRAME_M30
            min_num = 15
        elif run_type == "h1":
            # 十五分钟时间周期预算
            self.timeframe = mt5.TIMEFRAME_H1
            min_num = 15
        else:
            raise ValueError(f"周期参数异常, error: run_type = {run_type}")
        self.symbol = symbol
        # +1 多获取一条数据，避免最后一条获取不到，不过最后一波也不会交易
        self.need_data_count = 2000

    def get_price(self):
        # 获取当前utc时间
        now = datetime.now(pytz.utc)
        need_time =  now + timedelta(hours=1) + timedelta(minutes=1)
        # 添加服务器时区，这里和mt5 登陆账号有关
        data = mt5.copy_rates_from(self.symbol, self.timeframe, need_time, self.need_data_count)
        price_df = pd.DataFrame(data)
        # 将时间戳转化为年月日时分秒，格式为 = "year-month-day hour:min:second"
        # 这里添加一小时，是因为将数据时间修改为UTC+2,从而实现当日首次开仓时间在0点
        price_df['time'] = pd.to_datetime(price_df['time'] - 3600, unit='s')
        price_df = price_df.sort_values("time").reset_index(drop=True)
        now_price = price_df.iloc[-1]["close"]
        price_df["time"] = price_df["time"].astype("str")
        return price_df, now_price


if __name__ == '__main__':
    get_price_obj = GetSymbolPrice("m1")
    data, now_price = get_price_obj.get_price()
    print(data)