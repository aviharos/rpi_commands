#!/usr/bin/env python3
"""The main program 

This program loops and processes events
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
from EventHandler import EventHandler
from Storage import Storage
from Job import JobHandler
from Workstation import Workstation
from decode_message import decode_message

logger = getLogger(__name__)

def read_json(file: str):
    try:
        with open(file, "r") as f:
            object = json.load(f)
        return object
    except FileNotFoundError as error:
        raise FileNotFoundError(f"Error: file not found: {file}") from error
    except json.decoder.JSONDecodeError as error:
        raise ValueError(f"Error: invalid file specification: {file}") from error

def read_all_events():
    file = os.path.join("..", "events.json")
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
        print("./main.py /dev/ttyACM0")
        print("Replace /dev/ttyACM0 with the Arduino board that will send the event numbers")
        sys.exit(1)

    events = read_all_events()
    logger.info("Successfully read events")
    logger.debug(f"Events:\n{events}")
    objects = init_objects()
    logger.info("Successfully read objects")
    logger.debug(f"Objects:\n{objects}")
    eventHandler = EventHandler(events, objects)

    dev = sys.argv[1]
    ser = serial.Serial(dev, 9600, timeout=1)
    ser.reset_input_buffer()
    logger.info("Serial connection initialised")

    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8").rstrip()
                logger.info(f"Serial: incoming data: {line}")
                event_id, *args = decode_message(line)
                eventHandler.handle_event(event_id, *args)
    except KeyboardInterrupt:
        logger.info("Exiting...")

if __name__ == "__main__":
    main()

