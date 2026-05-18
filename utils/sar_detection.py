import numpy as np
import logging

from apps.users.models import *
from utils.send_email import send_email
from datetime import datetime, timedelta

def sar_detection_and_send_email(r):
    """
    检测当前全时间趋势，当处于同一趋势时，向vip发送邮件
    """
    now = datetime.now()
    logging.error(f"时间: {now}, 检测当前全时间趋势!")
    sap_data = [
        r.get("m1_XAUUSD_SAR"),
        r.get("m5_XAUUSD_SAR"),
        r.get("m15_XAUUSD_SAR"),
        r.get("m30_XAUUSD_SAR"),
        r.get("h1_XAUUSD_SAR"),
        r.get("h4_XAUUSD_SAR"),
    ]
    now_price = r.get("XAUUSD_now_price")
    if len(np.where(np.array(sap_data) > now_price)[0]) == 0:
        content_type = "下跌"
    elif len(np.where(np.array(sap_data) < now_price)[0]) == 0:
        content_type = "上涨"
    else:
        return

    before_send_email_time = r.get("before_send_email_time")
    if before_send_email_time and datetime.strptime(before_send_email_time, "%Y-%m-%d %H:%M:%S") < now - timedelta(hours=3):
        # 获取用户信息
        users = UserProfile.objects.filter(is_vip=True).exclude(email="")
        for user in users:
            send_email(user.email, content_type)
        r.set("before_send_email_time", now.strftime("%Y-%m-%d %H:%M:%S"))

