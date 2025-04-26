import redis.asyncio as redis
import asyncio

import json

from database.cruds import transfer_money, get_balance_from_login, unsuccessful_transaction


async def worker():
    r = redis.Redis(host='localhost', port=6379, db=0)
    while True:
        queue_data = await r.blpop('queue')
        if queue_data:
            value = json.loads(queue_data[1])
            current_balance = await get_balance_from_login(value[0])
            if current_balance < value[2]:
                await unsuccessful_transaction(value[0], value[1], value[2])
                continue
            await transfer_money(value[0], value[1], value[2])
        await asyncio.sleep(0.5)

async def start_worker():
    await asyncio.create_task(worker())