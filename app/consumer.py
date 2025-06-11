import os
import json
import logging

import pika
import asyncio
from dotenv import load_dotenv

from database.init_db import engine
from sqlalchemy.ext.asyncio import AsyncSession
from database.services.user_service import UserService
from database.services.transaction_service import TransactionService

load_dotenv()

async def process_message(body):
    value = json.loads(body)
    sender_login, receiver_login, amount = value

    async with AsyncSession(engine) as session:
        user_service = UserService(session)
        transaction_service = TransactionService(session)

        try:
            sender = await user_service.user_repo.get_user_by_login(sender_login)
            if not sender:
                await session.rollback()
                return

            if sender.balance < amount:
                await transaction_service.fail_transfer(sender_login, receiver_login, amount)
                await session.commit() 
                return

            success = await transaction_service.complete_transfer(sender_login, receiver_login, amount)
            if success:
                logging.info(f'Transfer completed successfully')
            else:
                logging.info(f'Transfer failed: {e}')
                await session.rollback()

        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()


def callback(ch, method, properties, body):
    asyncio.run(process_message(body))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def worker():
    params = pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST'))
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue='queue')
    channel.basic_consume(queue='queue', on_message_callback=callback)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        worker()
    except KeyboardInterrupt:
        print('Shutting down worker...')