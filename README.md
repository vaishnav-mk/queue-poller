# Queue Poller

This is a simple queue poller that polls a queue for messages and processes them. It's designed for both AWS SQS and Azure Storage Queues.

## Installation

```bash
cd queue_handler
pip install -r requirements.txt
```

## Usage

```bash
python main.py [--csp CSP] [--push-after-function BOOL]
```

* `--csp`: The cloud service provider. Valid values are `aws` and `azure`. Default is `azure`.
* `--push-after-function`: Whether to push the message and poll after each function call. Default is `False`.

## Example

```bash
python main.py --csp azure
```

```bash
python main.py --csp aws --push-after-function true
```

## Working

`main.py`:
* It first creates the list of functions to be executed.
* If the csp provided is azure, it:
  * gets the connection string based on the `resource_group` and `storage_account_name` provided.
  * writes the `connection_string` to the `monitoring_queue_config.json` file.
  * creates a queue based on the `queue_name` randomly generated.
  * writes the `queue_name` and `queue_url` to the `monitoring_queue_config.json` file.
  * executes the poller using a thread.
* If the csp provided is aws, it:
  * gets the queue url based on the `queue_name` provided.
  * stores the `queue_url` in the `monitoring_queue_config.json` file.
  * executes the poller using a thread.
* If `push_after_function` is `True`, it pushes the message to the queue after each function call.
* If `push_after_function` is `False`, it pushes the message to the queue after all the functions are executed.

sqs and azure pollers:
* It polls the queue for messages.
* Checks the message in the queue to see if all the functions have returned the execution output.
* If it has, it deletes the message from the queue and deletes the queue.
* If it hasn't, it writes the message received to the `output.json` file, sleeps for 2 seconds(by default), and polls again.

## Local Monitoring

### Installation

```bash
./setup.sh
```

* Go to `http://localhost:3000` to view the monitoring dashboard.
* Creates a websocket connection to the server to watch `output.json` for changes and updates the dashboard accordingly.
