"""Workstation object handler

Made from the abstract class OrionObject
"""

# Standard Library imports

# PyPI imports
import requests

# Custom imports
from OrionObject import OrionObject
from JobHandler import JobHandler


class Workstation(OrionObject):
    """Workstation Orion object 

    Attributes: 
        id (str): Orion id

    Usage:
        __init__:
            workstation = Workstation(id)

        turn_on(): 
            sets the available attribute of the object to True,
            also updates it in Orion

        turn_off():
            sets the available attribute of the object to False,
            also updates it in Orion
    """
    def __init__(self, session: requests.Session, id: str):
        super().__init__(session, id)
        self.available = False  # off by default
        self.reset_jobHandler()

    def reset_jobHandler(self):
        # getting a brand new JobHandler ensures that the JobHandler's counters are 0
        self.jobHandler = JobHandler(self.session, self.id)

    def update_available(self):
        self.update_attribute(attr_name="Available", attr_value=self.available)

    def turn_on(self):
        self.available = True
        self.update_available()

    def turn_off(self):
        self.available = False
        self.update_available()

    def handle_good_cycle(self):
        self.jobHandler.handle_good_cycle()

    def handle_reject_cycle(self):
        self.jobHandler.handle_reject_cycle()

