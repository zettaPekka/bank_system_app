import redis.asyncio as redis

import json


async def add_transaction_to_queue(from_uid: int, to_uid: int, amount: int):
    r = redis.Redis(host='localhost', port=6379, db=0)
    value = json.dumps([from_uid, to_uid, amount])
    await r.rpush('queue', value)