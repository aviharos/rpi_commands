"""JobHandler
"""

# Standard Library imports
import os

# PyPI imports
import requests

# Custom imports


MOMAMS_HOST = os.environ.get("MOMAMS_HOST")
if MOMAMS_HOST is None:
    raise ValueError("MOMAMS_HOST environment variable is not set")
IOTAGENT_HTTP_PORT = os.environ.get("IOTAGENT_HTTP_PORT")
if IOTAGENT_HTTP_PORT is None:
    raise ValueError("IOTAGENT_HTTP_PORT environment variable is not set")


class JobHandler:
    """JobHandler

    It is a group object because it does not belong to a specific Job.
    The Raspberry Pi does not know which Job is currently active on the Workstation.
    The Raspberry Pi only knows when a new job is started and how many
    cycles have been completed so far in the current job.
    Whenever good or reject parts are completed (a batch is considered uniform in this regard),
    the Raspberry Pi sends data to the IoT agent of MOMAMS
    informing it that a batch of good or reject parts is completed.

    Attributes:
        workstation_id (str): Orion id of the Job's workstation
        good_cycle_count (int): the number of good cycles so far
        reject_cycle_count (int): the number of reject cycles so far

    Usage:
        __init__:
            jobHandler = JobHandler(id)

        handle_good_cycle(type, counter):
            handles the event of good parts completed
            in a Workstation cycle 
            also sends the data to the IoT agent

        handle_reject_cycle(type, counter):
            handles the event of reject parts completed
            in a Workstation cycle 
            also sends the data to the IoT agent

        reset():
            reset the counters because of a new job

    """

    def __init__(self, workstation_id: str):
        self.workstation_id = workstation_id
        self.good_cycle_count = 0
        self.reject_cycle_count = 0

    def reset(self):
        self.good_cycle_count = 0
        self.reject_cycle_count = 0

    def send_request_to_iot_agent(self, type: str, counter: int):
        req = {
            "url": "",
            "method": "PUT",
            "headers": ["Content-Type: application/json"],
            "data": {},
            "transform": {"ws": "urn:ngsi_ld:Workstation:1", "ct": type, "cc": counter}
        }
        res = requests.post(url=f"http://{MOMAMS_HOST}:{IOTAGENT_HTTP_PORT}", json=req)
        if res.status_code != 204:
            raise RuntimeError(f"Sending request to the IoT agent failed. Response:{res}")

    def handle_good_cycle(self):
        self.good_cycle_count += 1
        self.send_request_to_iot_agent(type="good", counter=self.good_cycle_count)

    def handle_reject_cycle(self):
        self.reject_cycle_count += 1
        self.send_request_to_iot_agent(type="good", counter=self.reject_cycle_count)


