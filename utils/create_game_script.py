import os
import sys
import django

project_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MttmView.settings")
django.setup()


from apps.users.models import *
from datetime import datetime, timedelta

# 生成竞猜脚本

def get_weekdays_future(N, start_date=None):
    if start_date is None:
        start_date = datetime.now()
    elif isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    weekdays = []
    current_date = start_date
    for _ in range(N):
        if current_date.weekday() < 5:
            weekdays.append(current_date)
        current_date += timedelta(days=1)
    return weekdays


def create_game(symbol="XAUUSD"):
    dates = get_weekdays_future(N=365)
    print(dates)
    symbol = GameSymbol.objects.get(name=symbol, is_game=True)
    before_date = None
    for date in dates:
        if not before_date:
            before_date = date - timedelta(days=1)
        end_date = date + timedelta(days=1)
        GameCenter.objects.create(
            symbol=symbol,
            game_date=datetime(date.year, date.month, date.day, 6, 0, 0),
            start_time=datetime(before_date.year, before_date.month, before_date.day, 6, 0, 0),
            end_time =datetime(end_date.year, end_date.month, end_date.day, 6, 0, 0),
        )
        before_date = date


if __name__ == '__main__':
    create_game("DXY")