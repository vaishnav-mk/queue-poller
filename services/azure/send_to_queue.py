from contextlib import suppress
import os
import json
import time
from utils import read
from azure.storage.queue import QueueServiceClient, QueueClient, QueueMessage


def create_queue(queue_name: str) -> QueueClient:
    try:
        connection_string = read(csp="azure")["connection_string"]
        client = QueueServiceClient.from_connection_string(connection_string)
        queue_client = client.get_queue_client(queue_name)
        queue_client.create_queue()
        print(f"Queue created: {queue_client.url}")
        return queue_client.url
    except Exception as e:
        print(f"Error creating queue: {e}")
        raise e


def send_to_queue(data: dict, queue_name: str):
    try:
        connection_string = read(csp="azure")["connection_string"]
        client = QueueServiceClient.from_connection_string(connection_string)
        print(f"Queue name: {queue_name}")

        queue_client = client.get_queue_client(queue_name)
        message_body = json.dumps(data)
        print(f"Message body: {message_body}")

        queue_client.send_message(message_body)
        print(f"Message sent to queue: {queue_name}")
    except Exception as e:
        print(f"Error sending message to queue: {e}")
        raise e
