import re
from itertools import cycle

from rotest.core.block import TestBlock
from rotest.core.flow_component import BlockInput
from rotest.core.flow_component import BlockOutput

from air_to_breath_resources.resources import AirToBreathSetup


class StartProgram(TestBlock):
    setup: AirToBreathSetup = BlockInput()

    def test_method(self):
        self.setup.start_program()


class StopProgram(TestBlock):
    setup: AirToBreathSetup = BlockInput()

    def test_method(self):
        self.setup.stop_program()


class ValidateLogValues(TestBlock):
    setup: AirToBreathSetup = BlockInput()
    sensor = BlockInput()
    expected_value = BlockInput()

    def test_method(self):
        template = getattr(self, self.sensor).VALUE_TEMPLATE
        log_line = self.setup.log_reader.search(template)
        match = re.match(template, log_line)
        self.assertIsNotNone(match, f"couldnt find {template} in {log_line}")
        value = float(match.group(1))
        self.assertEqual(value, self.expected_value, f"got value={value}, expected={self.expected_value}")


class ClearBuffer(TestBlock):
    setup = BlockInput()

    def test_method(self):
        self.setup.log_reader.clear_buffer()


class InitializeSensorValuesBlock(TestBlock):
    expected_values = BlockOutput()

    def test_method(self):
        self.expected_values = {}


class SetSensorsValues(TestBlock):
    setup: AirToBreathSetup = BlockInput()
    sent_values = BlockInput(default=cycle([None]))
    sensors = BlockInput()
    expected_values: dict = BlockInput()

    def test_method(self):
        # TODO add feature to send couple of values to a sensor (like a sin wave) to simulate real scenario.
        for sensor, sent_value in zip(self.sensors, self.sent_values):
            sensor_obj = getattr(self.setup, sensor)
            value = sensor_obj.set_value(sent_value)
            self.expected_values[sensor] = value


class StartSensorSimulation(TestBlock):
    sensors = BlockInput()
    sent_values = BlockInput(default=None)
    low_values = BlockInput(default=None)
    high_values = BlockInput(default=None)

    expected_values = BlockOutput()

    def test_method(self):
        self.expected_values = {}
        # TODO zip longest?
        for sensor, sent_value, low_value, high_value in zip(self.sensors,
                                                             self.sent_values,
                                                             self.low_values,
                                                             self.high_values):
            sensor.start_simulate(sent_value, low_value, high_value)
            self.expected_values[sensor] = sensor.sent_value


class ChangeSensorValueSimulation(TestBlock):
    sensors = BlockInput()
    sensor_values = BlockInput()
    expected_values = BlockInput()

    def test_method(self):
        for sensor, sensor_value in zip(self.sensors, self.sensor_values):
            sensor.set_value(sensor_value)
            self.expected_values[sensor] = sensor_value


class UpperCrossSensorValue(TestBlock):
    sensors = BlockInput()
    expected_values = BlockInput()

    def test_method(self):
        for sensor in self.sensors:
            new_value = sensor.high_bound + 1
            self.expected_values[sensor] = new_value
            sensor.set_value(new_value)


class LowerCrossSensorValue(TestBlock):
    sensors = BlockInput()
    expected_values = BlockInput()

    def test_method(self):
        for sensor in self.sensors:
            new_value = sensor.low_bound - 1
            self.expected_values[sensor] = new_value
            sensor.set_value(new_value)


class NormalizeSensorValue(TestBlock):
    sensors = BlockInput()
    expected_values = BlockInput()

    def test_method(self):
        for sensor in self.sensors:
            new_value = (sensor.high_bound + sensor.low_bound) / 2.0
            self.expected_values.append(new_value)
            sensor.change_sensor_value(new_value)


class StopSensorSimulation(TestBlock):
    sensors = BlockInput()

    def test_method(self):
        for sensor in self.sensors:
            sensor.stop_simulate()


class ValidateSensors(TestBlock):
    setup: AirToBreathSetup = BlockInput()
    sensors: list = BlockInput()
    expected_values: dict = BlockInput()

    def validate(self, sensor, expected_value):
        template = getattr(self.setup, sensor).VALUE_TEMPLATE

        value = self.setup.log_reader.search(template)
        self.assertIsNotNone(value, f"Couldnt find {sensor} log line")
        self.assertEqual(float(value), expected_value, f"got value={value}, expected={expected_value}")

    def test_method(self):
        for sensor, expected_value in self.expected_values.items():
            expected_value = self.expected_values[sensor]
            self.validate(sensor, expected_value)
