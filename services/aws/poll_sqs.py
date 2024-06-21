import boto3
import json
import time
import os
from utils import load_output_data, check_completion, process_message, read

client = boto3.client("sqs")


def delete_queue(queue_url):
    try:
        client.delete_queue(QueueUrl=queue_url)
        print(f"Queue deleted: {queue_url}")
    except Exception as e:
        print(f"Error deleting queue: {e}")
        raise e


def poll_and_write(output_file="output.json", wait_time_seconds=2):
    data = read(csp="aws")
    queue_url = data["queue_url"]
    queue_name = data["queue_name"]
    try:
        output_data = load_output_data(output_file)

        while True:
            response = client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=wait_time_seconds,
            )

            for message in response.get("Messages", []):
                process_message(
                    message,
                    output_data,
                    output_file,
                    csp="aws",
                    queue_client=client,
                    queue_url=queue_url,
                )

            if check_completion(output_data, id=queue_name):
                print("got everything, exiting")
                delete_queue(queue_url)
                return

            time.sleep(wait_time_seconds)
    except Exception as e:
        print(f"Error polling SQS: {e}")
        raise e
