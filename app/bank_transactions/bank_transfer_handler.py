import redis.asyncio as redis

import json


async def add_transaction_to_queue(sender_login: int, receiver_login: int, amount: int):
    r = redis.Redis(host='localhost', port=6379, db=0)
    value = json.dumps([sender_login, receiver_login, amount])
    await r.rpush('queue', value)