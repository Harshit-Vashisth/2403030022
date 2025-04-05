from flask import Flask, jsonify as format_response, abort as reject_request
import requests as http_client
from collections import OrderedDict as NumberSequence
import time as timer
from threading import Lock as AccessController
from concurrent.futures import ThreadPoolExecutor as AsyncTaskManager

calculation_service = Flask(__name__)

# System configuration
DATA_WINDOW_CAPACITY = 10
EXTERNAL_API_ENDPOINT = "http://20.244.56.144/evaluation-service"
SUPPORTED_NUMBER_TYPES = {
    'prime': 'primes',
    'fibonacci': 'fibo',
    'even': 'even',
    'random': 'rand'
}
PROCESSING_DEADLINE = 0.5  # 500ms

# Data repository
number_repository = {
    'prime': NumberSequence(),
    'fibonacci': NumberSequence(),
    'even': NumberSequence(),
    'random': NumberSequence()
}
repository_lock = AccessController()

# Async task handler
task_handler = AsyncTaskManager(max_workers=4)


def retrieve_number_sequence(sequence_category):
    """Obtain numbers from external data provider"""
    api_endpoint = f"{EXTERNAL_API_ENDPOINT}/{sequence_category}"
    try:
        api_response = http_client.get(api_endpoint, timeout=PROCESSING_DEADLINE)
        if api_response.status_code == 200:
            return api_response.json().get('numbers', [])
    except (http_client.exceptions.RequestException, ValueError):
        pass
    return []


def compute_mean_value(number_collection):
    """Calculate arithmetic mean of numbers"""
    if not number_collection:
        return 0.0
    return round(sum(number_collection) / len(number_collection), 2)


def update_data_repository(category_id, incoming_numbers):
    """Maintain sliding window of numbers"""
    with repository_lock:
        data_store = number_repository[category_id]
        previous_numbers = list(data_store.keys())

        # Process new numbers
        for num in incoming_numbers:
            if num in data_store:
                # Update access order
                data_store.move_to_end(num)
            else:
                data_store[num] = None

        # Enforce capacity limits
        while len(data_store) > DATA_WINDOW_CAPACITY:
            data_store.popitem(last=False)

        current_numbers = list(data_store.keys())

        return previous_numbers, current_numbers


@calculation_service.route('/numeric-data/<string:category_id>', methods=['GET'])
def process_number_request(category_id):
    """Handle incoming number processing requests"""
    request_start = timer.time()

    # Validate request category
    if category_id not in SUPPORTED_NUMBER_TYPES:
        reject_request(400, description="Unsupported number category")

    # Asynchronously fetch numbers
    api_category = SUPPORTED_NUMBER_TYPES[category_id]
    future_task = task_handler.submit(retrieve_number_sequence, api_category)
    try:
        received_numbers = future_task.result(timeout=PROCESSING_DEADLINE)
    except TimeoutError:
        received_numbers = []

    # Update repository
    prior_state, updated_state = update_data_repository(category_id, received_numbers)

    # Compute statistics
    mean_value = compute_mean_value(updated_state)

    # Prepare output
    service_response = {
        "previousWindowState": prior_state,
        "currentWindowState": updated_state,
        "receivedNumbers": received_numbers,
        "averageValue": mean_value
    }

    # Verify processing time
    elapsed_time = timer.time() - request_start
    if elapsed_time > PROCESSING_DEADLINE:
        reject_request(500, description="Service timeout occurred")

    return format_response(service_response)


@calculation_service.errorhandler(400)
@calculation_service.errorhandler(500)
def handle_service_errors(error):
    """Standardized error responses"""
    return format_response({
        "errorMessage": error.description,
        "statusCode": error.code
    }), error.code


if __name__ == '__main__':
    calculation_service.run(host='0.0.0.0', port=9876, threaded=True)