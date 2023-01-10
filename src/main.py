#!/usr/bin/env python3
"""The main program 

This program loops and processes commands
by sending pre-configured data packet to the Orion broker.
"""

# Standard Library imports
import json
import sys
import time

# PyPI imports
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

    commandHandler = CommandHandler()

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
            logger.info("Exiting...")
            sys.exit()
        except Exception as error:
            logger.error(f"{error}")

if __name__ == "__main__":
    main()

