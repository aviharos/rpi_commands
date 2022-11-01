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

# PyPI imports
import serial

# custom imports
from Logger import getLogger
from CommandHandler import CommandHandler
from Storage import Storage
from JobHandler import JobHandler
from Workstation import Workstation

logger = getLogger(__name__)

def read_json(file: str):
    with open(file, "r") as f:
        object = json.load(f)
    return object

def read_all_commands():
    file = os.path.join("..", "commands.json")
    return read_json(file)

def init_objects():
    objects = {}
    files = glob.glob(os.path.join("..", "json", "*.json"))
    for file in files:
        object = read_json(file)
        id = object["id"]
        objects[id] = {}
        objects[id]["orion"] = object
        if object["type"] == "Storage":
            objects[id]["py"] = Storage(id, object["Capacity"]["value"], object["Step"]["value"], object["SubType"]["value"])
        if object["type"] == "Workstation":
            objects[id]["py"] = Workstation(id)
        if object["type"] == "Job":
            objects[id]["py"] = JobHandler(object["RefWorkstation"]["value"])
    return objects

def main():
    if len(sys.argv) != 2:
        print("Error: no device specified. Correct usage:")
        print("./main.py /dev/ttyUSB0")
        print("Replace /dev/ttyUSB0 with the Arduino board that will send the event numbers")
        sys.exit(1)

    commands = read_all_commands()
    logger.info("Successfully read commands")
    logger.debug(f"commands:\n{commands}")
    objects = init_objects()
    logger.info("Successfully read objects")
    logger.debug(f"Objects:\n{objects}")
    commandHandler = CommandHandler(commands, objects)

    dev = sys.argv[1]
    ser = serial.Serial(dev, 9600, timeout=1)
    ser.reset_input_buffer()
    logger.info("Serial connection initialised")

    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8").rstrip()
                logger.debug(f"Serial: incoming data: {line}")
                decoded_commands = json.loads(line)
                logger.debug(f"Decoded commands: {decoded_commands}")
                for event_id, arg in decoded_commands.items():
                    commandHandler.handle_command(event_id, arg)
    except KeyboardInterrupt:
        logger.info("Exiting...")

if __name__ == "__main__":
    main()

