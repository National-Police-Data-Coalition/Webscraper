import redis
from typing import Literal

class Producer:
    def __init__(self, backend_client):
        self.backend_client = backend_client

    def publish(self, channel:str, message:str):
        self.backend_client.publish(channel, message)

    def subscribe(self, channel:str):
        return self.backend_client.subscribe(channel)

class RedisPubClient:
    def __init__(self, host='redis', port=6379, db=0):
        self.connection = redis.Redis(host=host, port=port, db=db)

    def publish(self, channel:str, message:str):
        self.connection.publish(channel, message)

class PostgresPubSubClient:
    """This is a stub for a PostgreSQL Pub/Sub client. It is not implemented."""
    def __init__(self, host='localhost', port=5432, user='postgres', password='', database='postgres'):
        ...

class ProducerContainer:
    def __init__(self, db_type: Literal["REDIS"] = "REDIS"):
        if db_type == "REDIS":
            self.backend_client = RedisPubClient()
        else:
            self.backend_client = PostgresPubSubClient()

    def get_queue(self):
        return Producer(self.backend_client)