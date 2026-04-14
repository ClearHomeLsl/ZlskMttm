# ZlskMttm
# websocket 后台执行命令
nohup uvicorn MttmView.asgi:application --host 0.0.0.0 --port 8001 --reload > zlsk_wss.log 2>&1 &
# 定时任务后台执行命令
nohup python scripts/cron_task.py > cron_task.log 2>&1 &
# django启动命令
python manage.py runserver
# uwsgi启动命令
uwsgi --ini uwsgi.ini
# 查看websocket和cron的pid
ps aux | grep uvicorn
ps aux | grep cron_task
# 杀掉进程pid
kill <pid>
# 重启uwsgi
uwsgi --reload /deployer/ZlskMttm/MttmView_uwsgi.pid
