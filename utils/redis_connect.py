import redis


def get_redis_connect():
    pool = redis.ConnectionPool(
        host='127.0.0.1',
        port=6379,
        password='Qiuqi1201.',
        db=0,
        max_connections=10,    # 最大连接数
        decode_responses=True
    )
    r = redis.Redis(connection_pool=pool)
    return r