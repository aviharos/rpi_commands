"""CommandHandler 

Get an command_id (str), then manage everything related to that command

The command details are stored in commands.json

The main function passes the parsed objects to the CommandHandler 
that stores them in a dictionary called objects. 

Each objects manages its own specific methods that can be called by the commands. 

For example, the InjectionMoulding1.json object is parsed into a Workstation object. 
In the objects dictionary, the key will be "urn:ngsi_ld:Workstation:InjectionMoulding1"
and the value will be the Workstation object. 

Command "2", "3", "8", "10", "11" refer to the InjectionMoulding1 object. 
Whenever one of these commands is issued, the CommandHandler will get 
the Workstation object based by its id: "urn:ngsi_ld:Workstation:InjectionMoulding1". 
Then the Workstation's respective method will be called. 

For example, when command "10" is issued, 
the Workstation's handle_good_cycle command will be called.
"""

# Standard library imports

# Custom imports
from Storage import Storage
from Workstation import Workstation
from post_to_IoT_agent import post_to_IoT_agent


class CommandHandler():
    def __init__(self, commands:dict, objects: dict):
        self.commands = commands
        self.objects = objects

    def handle_command(self, command_id: str, arg=None):
        self.arg = arg
        if command_id not in self.commands:
            raise ValueError(f"command not specified in commands.json: {command_id}")
        self.command = self.commands[command_id]
        if self.is_command_special():
            self.handle_special_command()
        else:  # non special command
            self.handle_non_special_command()
        self.arg = None

    def is_command_special(self):
        return "special" in self.command.keys()

    def handle_special_command(self):
        req = self.command["request"]
        if self.arg is not None:
            req["data"] = self.arg
        post_to_IoT_agent(req)

    def handle_non_special_command(self):
        if "object_id" not in self.command:
            raise ValueError(f'Missing key: "object_id" in command: {self.command}')
        self.object_id = self.command["object_id"]
        if self.object_id not in self.objects:
            raise ValueError(f"Object not specified in a json file: {self.object_id}")
        self.object = self.objects[self.object_id]["py"]
        if isinstance(self.object, Storage):
            self.handle_storage()
        elif isinstance(self.object, Workstation):
            self.handle_workstation()

    def handle_storage(self):
        if self.command["type"] == "step":
            self.object.step()
        elif self.command["type"] == "reset":
            self.object.reset()
        else:
            raise NotImplementedError(f"command type {self.command['type']} not implemented for {self.object.id}")

    def handle_workstation(self):
        if self.command["type"] == "turn_on":
            self.object.turn_on()
        elif self.command["type"] == "turn_off":
            self.object.turn_off()
        elif self.command["type"] == "handle_good_cycle":
            self.object.handle_good_cycle()
        elif self.command["type"] == "handle_reject_cycle":
            self.object.handle_reject_cycle()
        elif self.command["type"] == "reset":
            self.object.reset()
            raise NotImplementedError(f"command type {self.command['type']} not implemented for {self.object.id}")

