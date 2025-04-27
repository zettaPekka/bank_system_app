import pika
from dotenv import load_dotenv

import os
import json


load_dotenv()

def add_transaction_to_queue(sender_login: int, receiver_login: int, amount: int):
    params = pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST'))
    with pika.BlockingConnection(params) as connection:
        with connection.channel() as ch:
            ch.queue_declare(queue='queue')
            value = json.dumps([sender_login, receiver_login, amount])
            ch.basic_publish(exchange='', routing_key='queue', body=value)