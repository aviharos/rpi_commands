#!/usr/bin/env python3
"""The main program 
"""

# Standard Library imports
import time
import sys

# PyPI imports
import RPi.GPIO as GPIO

# custom imports
from Logger import getLogger
from CommandHandler import CommandHandler
from Input import Input

logger = getLogger(__name__)

# constants
BAUD_RATE = 9600
BOOT_TIME = 20
DEBOUNCE_TIME_MILLISECONDS = 50
COMMAND_SEND_INTERVAL_MILLISECONDS = 60e3

# pins
MACHINE_AVAILABLE_PIN = -1
GOOD_PARTS_COMPLETED_PIN = -1
REJECT_PARTS_COMPLETED_PIN = -1

# setup
GPIO.setup(MACHINE_AVAILABLE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GOOD_PARTS_COMPLETED_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(REJECT_PARTS_COMPLETED_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

machine_available_input = Input(
    MACHINE_AVAILABLE_PIN,
    DEBOUNCE_TIME_MILLISECONDS,
    COMMAND_SEND_INTERVAL_MILLISECONDS,
)
good_parts_completed_input = Input(
    GOOD_PARTS_COMPLETED_PIN,
    DEBOUNCE_TIME_MILLISECONDS,
    COMMAND_SEND_INTERVAL_MILLISECONDS,
)
reject_parts_completed_input = Input(
    REJECT_PARTS_COMPLETED_PIN,
    DEBOUNCE_TIME_MILLISECONDS,
    COMMAND_SEND_INTERVAL_MILLISECONDS,
)

commandHandler = CommandHandler()


def handle_machine_availability():
    pass


def handle_good_part_completion():
    pass


def handle_reject_part_completion():
    pass


def loop():
    handle_machine_availability()
    handle_good_part_completion()
    handle_reject_part_completion()


def main():
    time.sleep(BOOT_TIME)

    while True:
        try:
            loop()
        except KeyboardInterrupt:
            logger.info("Exiting...")
            sys.exit()
        except Exception as error:
            logger.error(f"{error}")


if __name__ == "__main__":
    main()
