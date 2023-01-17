#!/usr/bin/env python3
"""The main program 

This program loops and processes commands
by sending pre-configured data packet to the Orion broker.
"""

# Standard Library imports
import errno
import json
import sys
import time

# PyPI imports
import serial

# custom imports
from Logger import getLogger
from CommandHandler import CommandHandler

logger = getLogger(__name__)

BAUD_RATE = 9600
BOOT_TIME = 20
SERIAL_RECHECK_PERIOD = 5

def check_args():
    if len(sys.argv) != 2:
        print("Error: no device specified. Correct usage:")
        print("./main.py /dev/ttyUSB0")
        print("Replace /dev/ttyUSB0 with the Arduino board that will send the event numbers")
        sys.exit(1)

def init_serial_device(dev):
    while True:
        try:
            ser = serial.Serial(dev, BAUD_RATE, timeout=1)
            ser.reset_input_buffer()
            logger.info("Serial connection initialised")
            return ser
        except serial.serialutil.SerialException as error:
            logger.error(f"Error: {error}")
            time.sleep(SERIAL_RECHECK_PERIOD)

def parse_concatenated_jsons(s: str):
    """This is necessary, because the Arduino might send
    2 or more sets of commands while the previous ones as processed like
    '{"1": None, "3": 0.45}{"1": None, "3": 0.45}' 
    These are concatenated jsons"""
    comma_separated = s.replace("}{", "},{")
    return json.loads(f"[{comma_separated}]")

def handle_set_of_commands(commandHandler, set_of_commands):
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

def handle_incoming_data_if_exists(commandHandler, ser):
    if ser.in_waiting > 0:
        line = ser.readline().decode("utf-8").rstrip()
        ser.reset_input_buffer()
        logger.debug(f"Serial: incoming data: {line}")
        decoded_commands = parse_concatenated_jsons(line)
        logger.debug(f"Decoded commands: {decoded_commands}")
        for set_of_commands in decoded_commands:
            handle_set_of_commands(commandHandler, set_of_commands)

def loop_as_long_as_serial_connection_is_active(commandHandler, ser):
    while True:
        try:
            handle_incoming_data_if_exists(commandHandler, ser)
        except OSError as error:
            logger.error(f"{error}")
            if error.errno == 5:
                # lost connection with serial device
                return
        except KeyboardInterrupt:
            raise
        except Exception as error:
            logger.error(f"{error}")

def main():
    check_args()
    time.sleep(BOOT_TIME)
    commandHandler = CommandHandler()
    dev = sys.argv[1]
    while True:
        try:
            ser = init_serial_device(dev)
            loop_as_long_as_serial_connection_is_active(commandHandler, ser)
        except KeyboardInterrupt:
            logger.info("Exiting...")
            sys.exit()
        except Exception as error:
            logger.error(f"{error}")


if __name__ == "__main__":
    main()

