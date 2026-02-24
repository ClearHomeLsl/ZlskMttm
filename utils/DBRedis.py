import redis
from MttmView.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD


def get_redis_connect():
    pool = redis.ConnectionPool(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        db=0,
        max_connections=10,    # 最大连接数
        decode_responses=True
    )
    r = redis.Redis(connection_pool=pool)
    return r