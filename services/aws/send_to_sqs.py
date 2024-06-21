import boto3
import json
import os
import time

client = boto3.client("sqs")


def create_queue(queue_name):
    try:
        response = client.create_queue(QueueName=queue_name)
        print(f'Queue created: {response["QueueUrl"]}')
        return response["QueueUrl"]
    except Exception as e:
        print(f"Error creating queue: {e}")
        raise e


def send_to_sqs(data, queue_url):
    try:
        if not data:
            raise ValueError("Data is empty")
        message_body = json.dumps(data)

        response = client.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body,
        )
        print(f'Message sent to SQS: {response["MessageId"]}')
    except Exception as e:
        print(f"Error sending message to SQS: {e}")
        raise e
