import redis.asyncio as redis
import asyncio

import json


async def worker():
    r = redis.Redis(host='localhost', port=6379, db=0)
    while True:
        queue_data = await r.blpop('queue')
        if queue_data:
            value = json.loads(queue_data[1])
            '''process value'''
        await asyncio.sleep(0.5)

async def start_worker():
    await asyncio.create_task(worker())