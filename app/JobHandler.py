"""JobHandler
"""

# Standard Library imports
import os

# PyPI imports
import requests

# Custom imports
from post_to_IoT_agent import post_to_IoT_agent


class JobHandler:
    """JobHandler

    It is an extraodinary object because we do not know which Job the JobHandler 
    refers to.
    The Raspberry Pi does not know which Job is currently active on the Workstation.
    The Raspberry Pi only knows when a new job is started and how many
    cycles have been completed so far in the current job.
    Whenever good or reject parts are completed (a batch is considered uniform in this regard),
    the Raspberry Pi sends data to the IoT agent of MOMAMS
    informing it that a batch of good or reject parts is completed.

    The JobHandler is not present directly in the CommandHandler's
    objects dict. It always exists as an attribute of one of the Workstation 
    objects. Whenever

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
    """

    def __init__(self, workstation_id: str):
        self.workstation_id = workstation_id
        self.good_cycle_count = 0
        self.reject_cycle_count = 0

    def send_request_to_iot_agent(self, type: str, counter: int):
        req = {
            "url": "",
            "method": "PUT",
            "headers": ["Content-Type: application/json"],
            "data": {},
            "transform": {"ws": self.workstation_id, "ct": type, "cc": counter}
        }
        post_to_IoT_agent(req)

    def handle_good_cycle(self):
        self.good_cycle_count += 1
        self.send_request_to_iot_agent(type="good", counter=self.good_cycle_count)

    def handle_reject_cycle(self):
        self.reject_cycle_count += 1
        self.send_request_to_iot_agent(type="reject", counter=self.reject_cycle_count)


