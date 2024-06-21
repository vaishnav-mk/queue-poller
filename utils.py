import json
import os


def append_or_create_entry(message_body, output_data):
    for entry in output_data:
        if entry["id"] == message_body["id"]:
            entry.update(message_body)
            break
    else:
        output_data.append(message_body)


def load_output_data(output_file):
    if os.path.exists(output_file):
        with open(output_file, "r") as file:
            output_data = json.loads(file.read() or "[]")
            # print(f"Loaded output data from file: {output_data}")
    else:
        output_data = []
    return output_data


def update_output_file(output_file, output_data):
    with open(output_file, "w") as file:
        file.write(json.dumps(output_data) + "\n")
    print(f"Updated output file with messages")


def check_completion(output_data, id):
    print(f"Checking completion with output data: {id}")
    if output_data is None:
        print("Output data is None. Returning False.")
        return False

    if not any(entry["id"] == id for entry in output_data):
        print(f"ID {id} not found in output data. Returning False.")
        return False

    for entry in output_data:
        if entry["id"] != id:
            continue
        if "node_list" in entry and all(node in entry for node in entry["node_list"]):
            print(f"All functions returned data for ID {entry['id']}")
        else:
            print(f"Waiting for functions to return data for ID {entry['id']}")
            return False

    return True


def process_message(message, output_data, output_file, **kwargs):
    csp = kwargs.get("csp")
    queue_client = kwargs.get("queue_client")
    message_body = None

    if csp == "azure":
        message_body = json.loads(message.content)
        queue_client.delete_message(message)
    elif csp == "aws":
        message_body = json.loads(message["Body"])
        queue_url = kwargs.get("queue_url")
        queue_client.delete_message(
            QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"]
        )
    append_or_create_entry(message_body, output_data)
    update_output_file(output_file, output_data)


def read(
    filepath="/home/wishee/work/sqs_new/queue_handler/monitoring_queue_config.json",
    csp="aws",
):
    try:
        with open(filepath, "r") as file:
            data = json.loads(file.read())
            print(f"Loaded config data: {data}")
            return data[csp]
    except Exception as e:
        print(f"Error reading file: {e}")
        raise e
