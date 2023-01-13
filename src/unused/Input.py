# Standard Library imports
import time

# PyPI imports
import RPi.GPIO as GPIO

class Input():
    def __init__(
            self,
            pin: int,
            debounce_time_milliseconds: int,
            command_send_interval_milliseconds: int):
        self.pin = pin
        self.debounce_time_milliseconds = debounce_time_milliseconds
        self.command_send_interval_milliseconds = command_send_interval_milliseconds
        self.state = GPIO.input(self.pin)
        self.reading = self.state
        self.last_change_time_milliseconds = time.time()
        self.is_command_sent = False
        self.is_changed = False

    def refresh(self):
        self.reading = GPIO.input(self.pin)
        if not self.is_changed:
            self.handle_change()
        if not self.is_changed:
            """necessary to check condition again 
            as it could change in check_if_changed"""
            self.handle_command_period()

    def handle_change(self):
        if (self.reading == self.state and
            self.get_milliseconds_since_last_change() >= self.debounce_time_milliseconds):
            self.state = self.reading
            self.is_changed = True
            self.is_command_sent = False

    def handle_command_period(self):
        if self.get_milliseconds_since_last_change() > self.command_send_interval_milliseconds:
            self.is_command_sent = False

    def get_milliseconds_since_last_change(self):
        return time.time() - self.last_change_time_milliseconds

    def set_command_is_sent(self):
        self.is_command_sent = True

    def acknowledge_change(self):
        self.is_changed = False
