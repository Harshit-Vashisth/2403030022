from fastapi import FastAPI, HTTPException
from collections import deque
import httpx
from typing import List
import time

app = FastAPI()

# Set fixed window size
WINDOW_SIZE = 10
number_window = deque(maxlen=WINDOW_SIZE)

# Mapping for the number type to its API URL
NUMBER_TYPE_URLS = {
    "p": "http://20.244.56.144/evaluation-service/primes",
    "f": "http://20.244.56.144/evaluation-service/fibo",
    "e": "http://20.244.56.144/evaluation-service/even",
    "r": "http://20.244.56.144/evaluation-service/rand"
}


@app.get("/numbers/{numberid}")
async def get_numbers(numberid: str):
    if numberid not in NUMBER_TYPE_URLS:
        raise HTTPException(status_code=400, detail="Invalid number ID. Use p, f, e, or r.")

    url = NUMBER_TYPE_URLS[numberid]

    # Save the state before fetching
    window_prev_state = list(number_window)

    fetched_numbers = []
    try:
        async with httpx.AsyncClient(timeout=0.5) as client:
            start = time.time()
            response = await client.get(url)
            duration = time.time() - start

            # If request took more than 500ms or failed
            if response.status_code != 200 or duration > 0.5:
                return {
                    "windowPrevState": window_prev_state,
                    "windowCurrState": list(number_window),
                    "numbers": [],
                    "avg": round(sum(number_window) / len(number_window), 2) if number_window else 0.0
                }

            data = response.json()
            fetched_numbers = data.get("numbers", [])

    except httpx.RequestError:
        return {
            "windowPrevState": window_prev_state,
            "windowCurrState": list(number_window),
            "numbers": [],
            "avg": round(sum(number_window) / len(number_window), 2) if number_window else 0.0
        }

    # Add new unique numbers to window
    for num in fetched_numbers:
        if num not in number_window:
            number_window.append(num)
            if len(number_window) == WINDOW_SIZE:
                break  # No need to add more

    window_curr_state = list(number_window)
    average = round(sum(number_window) / len(number_window), 2) if number_window else 0.0

    return {
        "windowPrevState": window_prev_state,
        "windowCurrState": window_curr_state,
        "numbers": fetched_numbers,
        "avg": average
    }
