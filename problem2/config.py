from collections import deque

# Mapping for valid input types
TYPE_URL_MAP = {
    'p': "http://20.244.56.144/evaluation-service/primes",
    'f': "http://20.244.56.144/evaluation-service/fibo",
    'e': "http://20.244.56.144/evaluation-service/even",
    'r': "http://20.244.56.144/evaluation-service/rand"
}

# Fixed size of the moving window
WINDOW_LIMIT = 10

# Storage container for window
number_window = deque(maxlen=WINDOW_LIMIT)
