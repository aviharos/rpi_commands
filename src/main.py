#!/usr/bin/env python3
"""The main program 

This program loops and processes commands
by sending pre-configured data packet to the Orion broker.
"""

# Standard Library imports
import glob
import json
import sys
import os
import time

# PyPI imports
import requests
import serial

# custom imports
from Logger import getLogger
from CommandHandler import CommandHandler
from Storage import Storage
from JobHandler import JobHandler
from Workstation import Workstation

logger = getLogger(__name__)

BAUD_RATE = 9600
BOOT_TIME = 20

RPI_COMMANDS_CONFIG = os.environ.get("RPI_COMMANDS_CONFIG")
if RPI_COMMANDS_CONFIG == None:
    logger.critical("Fatal: the RPI_COMMANDS_CONFIG environment variable is not set")

def read_json(file: str):
    with open(file, "r") as f:
        object = json.load(f)
    return object

def read_all_commands():
    file = os.path.join(RPI_COMMANDS_CONFIG, "commands.json")
    return read_json(file)

def init_objects(session: requests.Session):
    objects = {}
    files = glob.glob(os.path.join(RPI_COMMANDS_CONFIG, "json", "*.json"))
    for file in files:
        logger.debug(f"file: {file}")
        object = read_json(file)
        logger.debug(f"""file read: {file}
{object}""")
        id = object["id"]
        objects[id] = {}
        objects[id]["orion"] = object
        if "i40AssetType" not in object.keys():
            continue
        if object["i40AssetType"]["value"] == "Storage":
            objects[id]["py"] = Storage(session, id, object["capacity"]["value"], object["step"]["value"], object["i40AssetSubType"]["value"])
        if object["i40AssetType"]["value"] == "Workstation":
            objects[id]["py"] = Workstation(session, id)
        if object["i40AssetType"]["value"] == "Job":
            objects[id]["py"] = JobHandler(session, object["refWorkstation"]["value"])
    return objects

def parse_concatenated_jsons(s:str):
    comma_separated = s.replace("}{", "},{")
    return json.loads(f"[{comma_separated}]")

def main():
    if len(sys.argv) != 2:
        print("Error: no device specified. Correct usage:")
        print("./main.py /dev/ttyUSB0")
        print("Replace /dev/ttyUSB0 with the Arduino board that will send the event numbers")
        sys.exit(1)

    time.sleep(BOOT_TIME)

    session = requests.Session()

    commands = read_all_commands()
    logger.info("Successfully read commands")
    logger.debug(f"commands:\n{commands}")
    objects = init_objects(session)
    logger.info("Successfully read objects")
    logger.debug(f"Objects:\n{objects}")
    commandHandler = CommandHandler(session, commands, objects)

    dev = sys.argv[1]
    ser = serial.Serial(dev, BAUD_RATE, timeout=1)
    ser.reset_input_buffer()
    logger.info("Serial connection initialised")

    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8").rstrip()
                ser.reset_input_buffer()
                logger.debug(f"Serial: incoming data: {line}")
                """This is necessary, because the Arduino might send
                2 or more sets of commands while the previous ones as processed like
                '{"1": None, "3": 0.45}{"1": None, "3": 0.45}' 
                These are concatenated jsons"""
                decoded_commands = parse_concatenated_jsons(line)
                logger.debug(f"Decoded commands: {decoded_commands}")
                for set_of_commands in decoded_commands:
                    logger.debug(f"Processing set of commands: {set_of_commands}")
                    """The Arduino sends commands in sets
                    A set of commands consists of a dictionary
                    For example: {"1": None, "3": 0.45} means that
                    the Arduino sent 2 commands in a set:
                        command "1" with arg: null,
                        command "3" with arg: 0.45
                    Now let's handle each command separately"""
                    for command_id, arg in set_of_commands.items():
                        commandHandler.handle_command(command_id, arg)
        except KeyboardInterrupt:
            session.close()
            logger.info("Exiting...")
            sys.exit()
        except Exception as error:
            logger.error(f"{error}")

if __name__ == "__main__":
    main()

