import os
import sys
import django

project_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MttmView.settings")
django.setup()

import datetime
import ycnbc
from newspaper import Article
import time
from apps.news.models import FinanceNews
from utils.DBRedis import get_redis_connect
import pandas as pd


def get_news():
    news = ycnbc.News()
    finance_news = news.finance()  # 获取金融新闻列表
    df = pd.DataFrame(finance_news)
    df['time_clean'] = df['time'].str.replace(r'(\d+)(st|nd|rd|th)', r'\1', regex=True)
    df['datetime'] = pd.to_datetime(df['time_clean'], format='%a, %b %d %Y')
    now = df.iloc[0]["datetime"]
    df = df[df["datetime"] == now]

    print(f"时间: {datetime.datetime.now()}, 获取到 {len(df.shape[0])} 条新闻")

    for idx in range(df.shape[0]):
        url = df.iloc[idx]['link']
        title = df.iloc[idx]['headline']
        try:
            # 使用 newspaper3k 提取文章内容
            article = Article(url)
            article.download()
            article.parse()
            time.sleep(1)  # 避免请求过快
            obj, created = FinanceNews.objects.update_or_create(
                title=title,  # 判断条件
                release_time=article.publish_date,
                defaults={  # 需要更新或创建的字段
                    'content': article.text,
                    'news_link': url,
                    'add_time': datetime.datetime.now(),
                    'author': article.authors,
                }
            )
        except Exception as e:
            print(f"提取失败: {e}")
    r = get_redis_connect()
    r.set("before_last_up_time", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == '__main__':
    get_news()