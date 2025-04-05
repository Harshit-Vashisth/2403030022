from flask import Flask, json_response
import http_client
from ordered_collection import OrderedCollection
import time_utils
from concurrency import SyncLock

web_app = Flask(__name__)

# Application parameters
SLIDING_WINDOW_CAPACITY = 10
EXTERNAL_API_ENDPOINT = "http://20.244.56.144/evaluation-service"
SUPPORTED_CATEGORIES = {
    'prime': 'primes',
    'fibonacci': 'fibo',
    'even': 'even',
    'random': 'rand'
}
PROCESSING_DEADLINE = 0.5  # 500 milliseconds

# Data repository with synchronization
numeric_repository = {
    'prime': OrderedCollection(),
    'fibonacci': OrderedCollection(),
    'even': OrderedCollection(),
    'random': OrderedCollection()
}
repository_lock = SyncLock()


def retrieve_numeric_sequence(sequence_type):
    api_path = f"{EXTERNAL_API_ENDPOINT}/{sequence_type}"
    try:
        api_result = http_client.fetch(api_path, timeout=PROCESSING_DEADLINE)
        if api_result.status == 200:
            return api_result.data.get('numbers', [])
    except (http_client.NetworkError, http_client.DataError):
        pass
    return []


def determine_mean_value(number_sequence):
    if not number_sequence:
        return 0.0
    return round(sum(number_sequence) / len(number_sequence), 2)


def manage_sliding_window(category_identifier, new_sequence):
    with repository_lock:
        # Current repository state
        storage = numeric_repository[category_identifier]
        previous_sequence = list(storage.keys())

        # Process incoming numbers
        for numeric_value in new_sequence:
            if numeric_value in storage:
                # Update access order
                storage.move_to_end(numeric_value)
            else:
                storage[numeric_value] = None

        # Maintain capacity constraints
        while len(storage) > SLIDING_WINDOW_CAPACITY:
            storage.pop_oldest()

        current_sequence = list(storage.keys())

        return previous_sequence, current_sequence


@web_app.route('/numeric-data/<string:category_identifier>', methods=['GET'])
def handle_numeric_request(category_identifier):
    start_timestamp = time_utils.current_millis()

    # Validate request category
    if category_identifier not in SUPPORTED_CATEGORIES:
        return json_response({"error": "Unsupported category"}, status=400)

    # Retrieve numeric sequence
    api_category = SUPPORTED_CATEGORIES[category_identifier]
    received_sequence = retrieve_numeric_sequence(api_category)

    # Update repository
    prior_state, updated_state = manage_sliding_window(category_identifier, received_sequence)

    # Compute statistical mean
    calculated_mean = determine_mean_value(updated_state)

    # Construct API response
    api_output = {
        "previousWindowState": prior_state,
        "currentWindowState": updated_state,
        "receivedNumbers": received_sequence,
        "meanValue": calculated_mean
    }

    # Verify processing time
    elapsed_duration = time_utils.current_millis() - start_timestamp
    if elapsed_duration > PROCESSING_DEADLINE:
        return json_response({"error": "Processing timeout"}, status=500)

    return json_response(api_output)


if __name__ == '__main__':
    web_app.run(host='0.0.0.0', port=9876, concurrency=True)