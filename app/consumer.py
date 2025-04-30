import pika
import asyncio
from dotenv import load_dotenv

import json
import os

from database.database_manager import TransactionRepository, UserRepository


transaction_repo = TransactionRepository()
user_repo = UserRepository()

load_dotenv()

async def process(ch, method, properties, body):
    value = json.loads(body)
    current_balance = await user_repo.get_balance_from_login(value[0])
    if current_balance < value[2]:
        await transaction_repo.unsuccessful_transaction(value[0], value[1], value[2])
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return
    await transaction_repo.transfer_money(value[0], value[1], value[2])
    ch.basic_ack(delivery_tag=method.delivery_tag)

def callback(ch, method, properties, body):
    asyncio.run(process(ch, method, properties, body))

def worker():
    params = pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST'))
    with pika.BlockingConnection(params) as connection:
        with connection.channel() as ch:
            ch.queue_declare(queue='queue')
            ch.basic_consume(queue='queue', on_message_callback=callback)
            ch.start_consuming()

if __name__ == '__main__':
    try:
        worker()
    except KeyboardInterrupt:
        pass
