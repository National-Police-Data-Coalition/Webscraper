import redis
from typing import Literal


class RedisClient:
    def __init__(self, host='redis', port=6379, db=0):
        self.connection = redis.StrictRedis(host=host, port=port, db=db)

    def set(self, key, value, expiration_time=None):
        self.connection.set(key, value)
        if expiration_time:
            self.connection.expire(key, expiration_time)

    def get(self, key):
        return self.connection.get(key)
    
    def set_json(self, key:str, value:dict, expiration_time=None):
        self.connection.hset(key, mapping=value)
        if expiration_time:
            self.connection.expire(key, expiration_time)

    def get_json(self, key:str):    
        return self.connection.hgetall(key)


class PostgresClient:
    """This is a stub for a PostgreSQL client. It is not implemented."""
    def __init__(self, host='localhost', port=5432, user='postgres', password='', database='postgres'):
        ...


class ScrapeCache:
    def __init__(self, backend_client):
        self.backend_client = backend_client

    def set(self, key, value, expiration_time=None):
        self.backend_client.set(key, value, expiration_time)

    def get(self, key):
        return self.backend_client.get(key)
    
    def set_json(self, key:str, value:dict, expiration_time=None):
        self.backend_client.set_json(key, value, expiration_time)

    def get_json(self, key:str):
        return self.backend_client.get_json(key)


class ScrapeCacheContainer:
    def __init__(self, db_type: Literal["REDIS", "POSTGRES"] = "REDIS"):
        if db_type == "REDIS":
            self.backend_client = RedisClient()
        else:
            self.backend_client = PostgresClient()

    def get_cache(self):
        return ScrapeCache(self.backend_client)


"""
Exmaple Usage: 

if __name__ == "__main__":
    # Example of using the cache with dependency injection for Redis
    redis_container = ScrapeCacheContainer("REDIS")
    redis_cache = redis_container.get_cache()
    redis_cache.set('my_key', 'my_value', expiration_time=3600)
    redis_result = redis_cache.get('my_key')
    print(f"Redis Result: {redis_result}")
"""

