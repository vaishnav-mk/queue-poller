import json
import os
import time
from azure.storage.queue import QueueServiceClient, QueueClient
from utils import (
    read,
    load_output_data,
    check_completion,
    process_message,
)


def get_queue_service_client() -> QueueServiceClient:
    connection_string = read(csp="azure")["connection_string"]
    print(f"Connecting to Azure Queue with connection string: {connection_string}")
    return QueueServiceClient.from_connection_string(connection_string)


def delete_queue(queue_client: QueueClient):
    try:
        queue_client.delete_queue()
        print(f"Queue deleted: {queue_client.primary_endpoint}")
    except Exception as e:
        print(f"Error deleting queue: {e}")


def poll_and_write(output_file="output.json", wait_time_seconds=2):
    data = read(csp="azure")
    queue_name = data["queue_name"]
    try:
        queue_client = get_queue_service_client().get_queue_client(queue_name)
        print(f"Polling Azure Queue: {queue_client.primary_endpoint}")

        output_data = load_output_data(output_file)

        while True:
            messages = queue_client.receive_messages(
                messages_per_page=1, visibility_timeout=wait_time_seconds
            )
            for message in messages:
                process_message(
                    message,
                    output_data,
                    output_file,
                    queue_client=queue_client,
                    csp="azure",
                )

            if check_completion(output_data, id=queue_name):
                delete_queue(queue_client)
                return

            time.sleep(wait_time_seconds)
    except Exception as e:
        print(f"Error polling Azure Queue: {e}")
