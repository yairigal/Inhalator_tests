import json
import os
import socket
import time
from contextlib import contextmanager
from pathlib import Path
from threading import Thread


class BaseSensor:
    LOW_BOUND = NotImplemented
    HIGH_BOUND = NotImplemented

    def __init__(self):
        self._run = True
        self.low_value = self.LOW_BOUND
        self.high_value = self.HIGH_BOUND
        self.sent_value = (self.LOW_BOUND + self.HIGH_BOUND) / 2.0
        self.thread = None

    def send_values(self, sent_value):
        raise NotImplementedError

    def _simulate_main_thread(self):
        while self._run:
            self.send_values(self.sent_value)
            time.sleep(1)

    def start_simulate(self, sent_value=None, low_value=None, high_value=None):
        if self.thread is not None:
            raise RuntimeError("Simulation thread is already running")

        if self.sent_value is not None:
            self.sent_value = sent_value

        if self.low_value is not None:
            self.low_value = low_value

        if self.high_value is not None:
            self.high_value = high_value

        self._run = True
        self.thread = Thread(target=self._simulate_main_thread)
        self.thread.start()

    def change_sensor_value(self, new_value):
        self.sent_value = new_value

    def stop_simulate(self):
        self._run = False
        if self.thread is not None:
            self.thread.join()

        self.low_value = self.LOW_BOUND
        self.high_value = self.HIGH_BOUND
        self.thread = None

    # simulation with context manager
    def start_simulate_cm(self):
        self._run = True
        self.thread = Thread(target=self._simulate_main_thread)
        self.thread.start()

    def stop_simulate_cm(self):
        self._run = False
        self.thread.join()

    @contextmanager
    def simulate(self, low_value=None, high_value=None):
        if self.low_value is not None:
            self.low_value = low_value

        if self.high_value is not None:
            self.high_value = high_value

        try:
            self.start_simulate_cm()
            yield

        finally:
            self.stop_simulate_cm()
            self.low_value = self.LOW_BOUND
            self.high_value = self.HIGH_BOUND
            self.thread = None


class SocketSensor:
    CONFIG_PATH = Path(os.getenv('PYTHONPATH')) / 'air_to_breath' / 'configs' / 'config.json'

    ERROR_TEMPLATE = NotImplemented
    VALUE_TEMPLATE = NotImplemented

    def name(self):
        return NotImplemented

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        json_cfg = self.json_configuration()
        self.low_bound = json_cfg['threshold'][self.name]['min']
        self.high_bound = json_cfg['threshold'][self.name]['max']

    def json_configuration(self):
        with open(self.CONFIG_PATH) as f:
            return json.load(f)

    def set_value(self, sent_value: int, host, port):
        if sent_value is None:
            data = (self.high_bound + self.low_bound) / 2

        else:
            data = sent_value

        data_encoded = str(data).encode()

        self.socket.sendto(data_encoded, (host, port))
        return data

    def check_error(self, value):
        """Check if there should be an error."""
        return not self.low_bound <= value <= self.high_bound


class PressureSensor(SocketSensor):
    VALUE_TEMPLATE = "Pressure: (.*)"

    @property
    def name(self):
        return 'pressure'


class FlowSensor(SocketSensor):
    VALUE_TEMPLATE = "Flow: (.*)"

    @property
    def name(self):
        return 'flow'


class OxygenSensor(SocketSensor):
    VALUE_TEMPLATE = "WRONGLINE"

    @property
    def name(self):
        return 'oxygen'
