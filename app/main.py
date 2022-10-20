"""The main program 

This program loops and processes events
by sending pre-configured data packet to the Orion broker.
"""

# Standard Library imports
import json
import os

# PyPI imports

# custom imports
from Logger import getLogger

logger = getLogger(__name__)

def read_event(id: int):
    file = os.path.join("..", "events", f"{id}.json")
    try:
        with open(file, "r") as f:
            event = json.load(f)
        return event
    except FileNotFoundError as error:
        raise FileNotFoundError(f"Error: event {id} is not specified: {error}")
    except json.decoder.JSONDecodeError as error:
        raise ValueError(f"Error: event {id} is specified incorrectly: {error}")

def loop():
    """ Everything that needs to be done in each loop. """
    pass

def main():
    pass

if __name__ == "__main__":
    main()

