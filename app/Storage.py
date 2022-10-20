"""Storage object handler

Made from the abstract class OrionObject
"""

# Standard Library imports

# Custom imports
from OrionObject import OrionObject


class Storage(OrionObject):
    """Storage Orion object 

    Attributes: 
        id (str): Orion id
        capacity (int): capacity
        counter (int): the current number of items in the Storage
        batch_size (int): the change in the counter when a batch of items 
            is put in or is taken away
        type: "emptying" or "filling"
            If a storage is normally full and items are taken from it
                and needs to be reloaded when resetting,
                it is an "emptying" type Storage. 
            If a storage is normally empty and items are put into it
                and needs to be emptied when resetting,
                it is a "filling" type Storage.

    Usage:
        __init__:
            storage = Storage(id, capacity, batch_size, type)
                example:
                    coverMagnetStorage = Storage("urn:ngsi_ld:Storage:CoverMagnetStorage1", 288, -8, "emptying")
                        A Storage of 288, -8 items per batch, needs to be filled when empty.

        step(): 
            updates the storage's counter by adding to it the batch_size
            also updates the counter in Orion

        reset():
            resets the storage's counter, also updates it in Orion

    """
    def __init__(self, id: str, capacity: int, batch_size: int, type: str):
        super().__init__(id)
        self.capacity = capacity
        self.batch_size= batch_size
        self.type = type
        if self.type == "emptying":
            self.counter = self.capacity
        elif self.type == "filling":
            self.counter = 0
        else:
            raise ValueError(f'Invalid type: {type}: supported types: "emptying", "filling"')

    def update_counter(self):
        self.update_attribute(attr_name="Counter", attr_value=self.counter)

    def step(self):
        self.counter += self.batch_size
        self.update_counter()

    def reset(self):
        if self.type == "emptying":
            self.counter = self.capacity
        elif self.type == "filling":
            self.counter = 0
        else:
            raise NotImplementedError()
        self.update_counter()


