"""An abstract Orion object class 

Used by Storage.py, Workstation.py, Job.py
"""

# Standard Library imports
from abc import ABC

# Custom imports
import Orion


class OrionObject(ABC):
    def __init__(self, id):
        self.id = id

    def update_attribute(self, attr_name, attr_value):
        """update attribute in Orion

        since the Orion broker stores data in JSON objects,
        we need to convert some values to be compatible with it"""
        if attr_value == None:
            attr_value = "null"
        if attr_value == True:
            attr_value = "true"
        if attr_value == False:
            attr_value = "false"
        Orion.update_attribute(self.id, attr_name, attr_value)
