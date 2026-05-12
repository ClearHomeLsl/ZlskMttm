import time

from apps.users.models import *
from datetime import datetime


def check_freeze():
    """
    每一小时检测一次解冻
    """
    now = datetime.now()
    print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} 执行代理冻结金额解冻。")
    freeze_logs = UserActiveWalletLog.objects.filter(is_thaw=False, thaw_time__lte=datetime.now())
    for log in freeze_logs:
        active_wallet = UserActiveWallet.objects.get(user=log.relationship.active)
        active_wallet.freeze -= log.amount
        active_wallet.balance += log.amount
        active_wallet.save()
        log.is_thaw = True
        log.save()
        print(f"{log.relationship.active.username} 冻结金额已解冻，解冻金额为: {log.amount}")
    print("=========================end=========================")


if __name__ == '__main__':
    while True:
        check_freeze()
        time.sleep(3600)