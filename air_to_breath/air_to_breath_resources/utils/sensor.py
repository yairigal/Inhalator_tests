import time
from contextlib import contextmanager
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


class PressureSensor(BaseSensor):
    LOW_BOUND = 0
    HIGH_BOUND = 5

    def send_values(self):
        pass


class FlowSensor(BaseSensor):
    LOW_BOUND = 0
    HIGH_BOUND = 5

    def send_values(self):
        pass


class OxygenSensor(BaseSensor):
    LOW_BOUND = 0
    HIGH_BOUND = 5

    def send_values(self):
        pass
