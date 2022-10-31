import os

import requests

from Logger import getLogger

logger = getLogger(__name__)

MOMAMS_HOST = os.environ.get("MOMAMS_HOST")
if MOMAMS_HOST is None:
    raise ValueError("MOMAMS_HOST environment variable is not set")
IOTAGENT_HTTP_PORT = os.environ.get("IOTAGENT_HTTP_PORT")
if IOTAGENT_HTTP_PORT is None:
    raise ValueError("IOTAGENT_HTTP_PORT environment variable is not set")

def post_to_IoT_agent(req: dict):
    logger.debug(f"post_to_IoT_agent: req: {req}")
    logger.debug(f"post_to_IoT_agent: url: http://{MOMAMS_HOST}:{IOTAGENT_HTTP_PORT}")
    res = requests.post(url=f"http://{MOMAMS_HOST}:{IOTAGENT_HTTP_PORT}", headers={"Content-Type": "application/json"}, json=req)
    if res.status_code != 204:
        raise RuntimeError(f"Sending request to the IoT agent failed. Response:{res}")

