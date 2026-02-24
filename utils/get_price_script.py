# 用于windows系统中获取产品实时价格

import redis
import json
import time

from utils.basic_data import *
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime

symbol = "XAUUSD"
# 方式2：使用连接池（推荐用于生产环境）
pool = redis.ConnectionPool(
    host='192.168.50.248',
    port=6379,
    password='Qiuqi1201.',
    db=0,
    max_connections=10,    # 最大连接数
    decode_responses=True
)
r = redis.Redis(connection_pool=pool)



def m1_price_job_2s():
    """
    XAUUSD 一分钟的K线图数据更新
    :return:
    """
    m1_run_obj = GetSymbolPrice("m1", symbol=symbol)
    now_price_df, now_price = m1_run_obj.get_price()
    data = now_price_df.to_dict('records')
    data = json.dumps(data)
    r.set("m1_XAUUSD_price", data)
    r.set("XAUUSD_now_price", now_price)
    print(f"北京时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}， {symbol} m1 数据更新！！")
    print("===" * 20)



def m5_price_job_4s():
    """
    XAUUSD 一分钟的K线图数据更新
    :return:
    """
    m5_run_obj = GetSymbolPrice("m5", symbol=symbol)
    now_price_df, now_price = m5_run_obj.get_price()
    data = now_price_df.to_dict('records')
    data = json.dumps(data)
    r.set("m5_XAUUSD_price", data)
    print(f"北京时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}， {symbol} m5 数据更新！！")
    print("===" * 20)


def m15_price_job_5s():
    """
    XAUUSD 一分钟的K线图数据更新
    :return:
    """
    m15_run_obj = GetSymbolPrice("m15", symbol=symbol)
    now_price_df, now_price = m15_run_obj.get_price()
    data = now_price_df.to_dict('records')
    data = json.dumps(data)
    r.set("m15_XAUUSD_price", data)
    print(f"北京时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}， {symbol} m15 数据更新！！")
    print("===" * 20)


def m30_price_job_10s():
    """
    XAUUSD 一分钟的K线图数据更新
    :return:
    """
    m30_run_obj = GetSymbolPrice("m30", symbol=symbol)
    now_price_df, now_price = m30_run_obj.get_price()
    data = now_price_df.to_dict('records')
    data = json.dumps(data)
    r.set("m30_XAUUSD_price", data)
    print(f"北京时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}， {symbol} m30 数据更新！！")
    print("===" * 20)


def h1_price_job_15s():
    """
    XAUUSD 一分钟的K线图数据更新
    :return:
    """
    h1_run_obj = GetSymbolPrice("h1", symbol=symbol)
    now_price_df, now_price = h1_run_obj.get_price()
    data = now_price_df.to_dict('records')
    data = json.dumps(data)
    r.set("h1_XAUUSD_price", data)
    print(f"北京时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}， {symbol} h1 数据更新！！")
    print("===" * 20)



if __name__ == "__main__":

    # 配置调度器，允许任务并发执行
    executors = {
        'default': ThreadPoolExecutor(5)  # 最多5个线程并发执行
    }

    job_defaults = {
        'max_instances': 3,  # 允许最多3个实例同时运行
    }

    scheduler = BackgroundScheduler(
        executors=executors,
        job_defaults=job_defaults
    )

    # 2. 添加任务，使用IntervalTrigger定义精确间隔
    scheduler.add_job(m1_price_job_2s, IntervalTrigger(seconds=2), id='m1_price_job_2s')
    # scheduler.add_job(m5_price_job_4s, IntervalTrigger(seconds=4), id='m5_price_job_4s')
    # scheduler.add_job(m15_price_job_5s, IntervalTrigger(seconds=5), id='m15_price_job_5s')
    # scheduler.add_job(m30_price_job_10s, IntervalTrigger(seconds=10), id='m30_price_job_10s')
    # scheduler.add_job(h1_price_job_15s, IntervalTrigger(seconds=15), id='h1_price_job_15s')


    # 3. 启动调度器
    scheduler.start()
    print("APScheduler 定时任务已启动...")

    # 4. 保持主程序运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在关闭调度器...")
        scheduler.shutdown()
        print("程序退出")