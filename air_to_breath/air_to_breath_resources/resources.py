"""All air_to_breath project resources."""
import time

from rotest.management.base_resource import BaseResource

from contextlib import contextmanager
from threading import Thread

from air_to_breath_resources.utils.log_parser import LogReader
from air_to_breath_resources.utils.pressure_sensor import PressureSensor

from air_to_breath_resources.utils.sensor import FlowSensor
from air_to_breath_resources.utils.sensor import OxygenSensor


class AirToBreathSetup(BaseResource):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log_reader = LogReader()
        self.pressure = PressureSensor()
        self.flow = FlowSensor()
        self.oxygen = OxygenSensor()

    def connect(self):
        self.logger.debug("Starting log reader")
        self.log_reader.start_logger()

    def finalize(self):
        self.logger.debug("Stopping log reader")
        self.log_reader.stop()