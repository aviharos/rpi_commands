"""Workstation object handler

Made from the abstract class OrionObject
"""

# Standard Library imports

# Custom imports
from OrionObject import OrionObject


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
    def __init__(self, id: str):
        super().__init__(id)
        self.available = False  # off by default

    def update_available(self):
        self.update_attribute(attr_name="Available", attr_value=self.available)

    def turn_on(self):
        self.available = True
        self.update_available()

    def turn_off(self):
        self.available = False
        self.update_available()

