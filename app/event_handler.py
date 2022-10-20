"""Event handler 

Get an event number, then manage everything related to that event
"""

# Standard library imports

# Custom imports
from Storage import Storage
from Workstation import Workstation
from Job import JobHandler



class EventHandler():
    def __init__(self, events:dict, objects: dict):
        self.events = events
        self.objects = objects

    def handle_event(self, event_id: int):
        self.event = self.events[event_id]
        self.object_id = self.event["object_id"]
        self.object = self.objects[self.object_id]
        if isinstance(self.object, Storage):
            self.handle_storage()
        elif isinstance(self.object, Workstation):
            self.handle_workstation()
        elif isinstance(self.object, JobHandler):
            self.handle_jobhandler()

    def handle_storage(self):
        if self.event["type"] == "step":
            self.object.step()
        elif self.event["type"] == "reset":
            self.object.reset()
        else:
            raise NotImplementedError(f"Event type {self.event['type']} not implemented for {self.object.id}")

    def handle_workstation(self):
        if self.event["type"] == "turn_on":
            self.object.turn_on()
        elif self.event["type"] == "turn_off":
            self.object.turn_off()
        else:
            raise NotImplementedError(f"Event type {self.event['type']} not implemented for {self.object.id}")

    def handle_jobhandler(self):
        if self.event["type"] == "handle_good_cycle":
            self.object.handle_good_cycle()
        elif self.event["type"] == "handle_reject_cycle":
            self.object.handle_reject_cycle()
        elif self.event["type"] == "reset":
            self.object.reset()
        else:
            raise NotImplementedError(f"Event type {self.event['type']} not implemented for {self.object.id}")

