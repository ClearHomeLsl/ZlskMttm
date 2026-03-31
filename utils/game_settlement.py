# 每天早上6点结算竞猜中心

import os
import sys
import django
import json

project_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MttmView.settings")
django.setup()


from apps.users.models import *
from datetime import datetime, timedelta
from utils.DBRedis import get_redis_connect
import pandas as pd

def end_game():
    now = datetime.now()
    games = GameCenter.objects.filter(end_time__date=now.date(),result__isnull=True)
    r = get_redis_connect()
    for game in games:
        symbol = game.symbol.name
        trade_day = game.game_date.date().strftime("%Y-%m-%d")
        data = r.get(f"m30_{symbol}_price")
        if not data:
            print(f"未获取到{symbol}报价数据")
            continue
        data = json.loads(data)
        df = pd.DataFrame(data)

        trade_df = df[df["time"].str.contains(trade_day)]
        if trade_df.shape[0] <= 0:
            print(f"未获取到{symbol}{trade_day}交易日的报价数据")
            continue
        open_price = trade_df.iloc[0]["open"]
        close_price = trade_df.iloc[-1]["close"]
        if open_price < close_price:
            # 开盘价低于收盘价，那么视为涨
            result = 1
        else:
            # 开盘价高于或等于收盘价，那么视为跌
            result = 2
        # 处理竞猜结果
        game.result = result
        game.open_price = open_price
        game.close_price = close_price
        game.save()
        # 处理用户竞猜输赢
        signup_games = UserGameSignUp.objects.filter(game_center=game, is_end=False)
        print(signup_games)
        for signup in signup_games:
            if signup.guess == result:
                # 竞猜赢
                signup.result = 1
                signup.is_end = True
                signup.end_time = now
                signup.save()
                # 给用户增加积分
                user = signup.user
                point = signup.point
                # 竞猜胜利，积分翻倍
                add_point = point * 2
                # 积分变动流水
                PointRecord.objects.create(
                    user=user,
                    old_point=user.point,
                    add_point=add_point,
                    new_point=(user.point + add_point),
                    change_oper=2,
                )
                user.point += signup.point
                user.save()
                # TODO 添加通知信息
            else:
                signup.result = 2
                signup.is_end = True
                signup.end_time = now
                signup.save()
        print(f"产品:{symbol},交易日:{trade_day}, 竞猜结算！ ")
    print("=====" * 15)


if __name__ == '__main__':
    end_game()