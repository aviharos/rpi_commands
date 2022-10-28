import os

import requests

MOMAMS_HOST = os.environ.get("MOMAMS_HOST")
if MOMAMS_HOST is None:
    raise ValueError("MOMAMS_HOST environment variable is not set")
IOTAGENT_HTTP_PORT = os.environ.get("IOTAGENT_HTTP_PORT")
if IOTAGENT_HTTP_PORT is None:
    raise ValueError("IOTAGENT_HTTP_PORT environment variable is not set")

def post_to_IoT_agent(req: dict):
    res = requests.post(url=f"http://{MOMAMS_HOST}:{IOTAGENT_HTTP_PORT}", json=req)
    if res.status_code != 204:
        raise RuntimeError(f"Sending request to the IoT agent failed. Response:{res}")

