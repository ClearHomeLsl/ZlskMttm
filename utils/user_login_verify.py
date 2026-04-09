from rest_framework.response import Response
from utils.DBRedis import get_redis_connect
from apps.users.models import UserProfile
from channels.db import database_sync_to_async

def login_verify(auth_token):
    if not auth_token:
        return True, Response({"msg": "未登录", "code": "1004", "response_type": "error"})
    # 解析 cookie
    parts = auth_token.split('_')
    if len(parts) != 3:
        return True, Response({"msg": "无效token", "code": "1004", "response_type": "error"})
    user_id = parts[1]
    username = parts[2]
    # 验证 redis
    r = get_redis_connect()
    stored_token = r.get(username)
    if stored_token != auth_token:
        print(stored_token, auth_token)
        return True, Response({"msg": "token无效", "code": "1004", "response_type": "error"})
    # 获取用户
    try:
        user = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        return True, Response({"msg": "用户不存在", "code": "1003", "response_type": "error"})
    return False, user


@database_sync_to_async
def login_verify_async(auth_token):
    if not auth_token:
        return True, Response({"msg": "未登录", "code": "1004", "response_type": "error"})
    # 解析 cookie
    parts = auth_token.split('_')
    if len(parts) != 3:
        return True, Response({"msg": "无效token", "code": "1004", "response_type": "error"})
    user_id = parts[1]
    username = parts[2]
    # 验证 redis
    r = get_redis_connect()
    stored_token = r.get(username)
    if stored_token != auth_token:
        print(stored_token, auth_token)
        return True, Response({"msg": "token无效", "code": "1004", "response_type": "error"})
    # 获取用户
    try:
        user = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        return True, Response({"msg": "用户不存在", "code": "1003", "response_type": "error"})
    return False, user

