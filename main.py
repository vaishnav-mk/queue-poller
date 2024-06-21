from functions.function_a import function_a
from functions.function_b import function_b
from functions.function_c import function_c
from functions.function_d import function_d
from functions.function_e import function_e
from functions.function_f import function_f

from services.aws.send_to_sqs import (
    send_to_sqs as send_to_aws_queue,
    create_queue as create_aws_queue,
)
from services.aws.poll_sqs import poll_and_write as poll_aws_queue

from services.azure.send_to_queue import (
    send_to_queue as send_to_azure_queue,
    create_queue as create_azure_queue,
)

from services.azure.poll_queue import poll_and_write as poll_azure_queue

import argparse
import string
import random
import sys
import threading
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument(
    "--push-after-function",
    help="True or False for pushing after each function/step",
    default=False,
    type=bool,
)
parser.add_argument(
    "--csp",
    help="aws or azure for selecting cloud provider",
    default="azure",
    type=str,
)


def randomString(stringLength):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(stringLength))


def call_and_send(func, data, queue_url, push_to_azure, push_after_each):
    func(data)
    print(f"{func.__name__} called")

    if not push_after_each:
        return

    if push_to_azure:
        queue_name = queue_url.split("/")[-1]
        print(f"Sending data to Azure Queue: {queue_name}")
        send_to_azure_queue(data, queue_name)
        print(f"Data sent to Azure Queue after {func.__name__}")
    else:
        send_to_aws_queue(data, queue_url)
        print(f"Data sent to AWS SQS after {func.__name__}")


def write(data, filepath="monitoring_queue_config.json"):
    try:
        with open(filepath, "w") as file:
            json.dump(data, file)
            print(f"Data written to file: {filepath}")
    except Exception as e:
        print(f"Error writing to file: {e}")
        raise e


if __name__ == "__main__":
    args = parser.parse_args()

    push_after_each = args.push_after_function
    cloud_provider = args.csp

    print(f"Push after each: {push_after_each}")
    print(f"Cloud provider: {cloud_provider}")

    queue_name = randomString(5)

    functions = [function_a, function_b, function_c, function_d, function_e, function_f]
    data = {
        "id": queue_name,
        "node_list": [func.__name__ for func in functions],
        "provider": "azure" if cloud_provider == "azure" else "aws",
    }

    queue_data = None
    queue_url = None

    if cloud_provider == "azure":
        resource_group = "xfaasLogcentralindia"
        storage_account_name = "xfaaslogcentralindia123"
        connection_string_command = f"az storage account show-connection-string --name {storage_account_name} --resource-group {resource_group} --query connectionString"
        stream = os.popen(connection_string_command)
        connection_string = stream.read().strip()

        write(
            {"azure": {"connection_string": connection_string}},
        )

        queue_url = create_azure_queue(queue_name)
        queue_data = {
            "azure": {
                "connection_string": connection_string,
                "queue_name": queue_name,
                "queue_url": queue_url,
            }
        }
        poller = threading.Thread(target=poll_azure_queue)
    else:
        queue_url = create_aws_queue(queue_name)
        queue_data = {
            "aws": {
                "queue_name": queue_name,
                "queue_url": queue_url,
            }
        }
        poller = threading.Thread(target=poll_aws_queue)

    write(queue_data)

    poller.daemon = True
    poller.start()

    for func in functions:
        call_and_send(func, data, queue_url, cloud_provider == "azure", push_after_each)

    if not push_after_each:
        if cloud_provider == "azure":
            queue_name = queue_url.split("/")[-1]
            print(f"Sending data to Azure Queue: {queue_name}")
            send_to_azure_queue(data, queue_name)
            print("Data sent to Azure Queue at the end")
        else:
            send_to_aws_queue(data, queue_url)
            print("Data sent to AWS SQS at the end")

    poller.join()

    print(f"Data: {data}")
