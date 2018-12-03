import redis


def create_redis_client(redis_connection_string: str):
    connection_pool = redis.BlockingConnectionPool.from_url(redis_connection_string)
    redis_client = redis.Redis(connection_pool=connection_pool)
    return redis_client
