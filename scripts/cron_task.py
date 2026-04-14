import os
import sys
import django

project_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MttmView.settings")
django.setup()



from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import pytz
from utils.push_price import broadcast_kline_update
from utils.DBRedis import get_redis_connect
from utils.game_settlement import end_game
from utils.save_price import SavePrice

r = get_redis_connect()

# 创建调度器
scheduler = BlockingScheduler(timezone=pytz.timezone('Asia/Shanghai'))  # 设置时区为北京时间


# 多重时间框架价格推送 m1
scheduler.add_job(func=broadcast_kline_update,trigger='interval',seconds=1,id='push_gold_m1',name='XAUUSDm1', args=["XAUUSD", "m1", r])
# m5
scheduler.add_job(func=broadcast_kline_update,trigger='interval',seconds=1,id='push_gold_m5',name='XAUUSDm5', args=["XAUUSD", "m5", r])
# m15
scheduler.add_job(func=broadcast_kline_update,trigger='interval',seconds=1,id='push_gold_m15',name='XAUUSDm15', args=["XAUUSD", "m15", r])
# m30
scheduler.add_job(func=broadcast_kline_update,trigger='interval',seconds=1,id='push_gold_m30',name='XAUUSDm30', args=["XAUUSD", "m30", r])
# h1
scheduler.add_job(func=broadcast_kline_update,trigger='interval',seconds=1,id='push_gold_h1',name='XAUUSDh1', args=["XAUUSD", "h1", r])
# TODO多重时间框架点位推送
# scheduler.add_job(func=broadcast_kline_update,trigger='interval',seconds=1,id='push_price',name='每秒执行任务')
# 每日竞猜结算，每天7点执行
scheduler.add_job(func=end_game,trigger='cron',hour=7,minute=0,id='end_game',name='结算交易大赛', args=[r])
# 保存前一日数据，每天0点执行，加入23号0点保存21日的数据
scheduler.add_job(func=SavePrice,trigger='cron',hour=0,minute=0,id='save_price',name='保存历史价格', args=[r])




for job in scheduler.get_jobs():
    print(f"任务ID: {job.id}")
    print(f"任务名称: {job.name}")
    print(f"下次执行时间: {job.next_run_time}")
    print("-" * 30)

# 启动调度器（阻塞模式）
try:
    scheduler.start()
except KeyboardInterrupt:
    print("\n定时任务已停止")