import re
from itertools import cycle

from rotest.core.block import TestBlock
from rotest.core.flow_component import BlockInput
from rotest.core.flow_component import BlockOutput

from air_to_breath_resources.resources import AirToBreathSetup


class StartProgram(TestBlock):
    setup: AirToBreathSetup = BlockInput()

    expected_values = BlockOutput()

    def test_method(self):
        self.setup.start_program()
        self.expected_values = {}


class StopProgram(TestBlock):
    setup: AirToBreathSetup = BlockInput()

    def test_method(self):
        self.setup.stop_program()


class ClearBuffer(TestBlock):
    setup = BlockInput()

    def test_method(self):
        self.setup.log_reader.clear_buffer()


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


class ValidateSensorsError(TestBlock):
    setup: AirToBreathSetup = BlockInput()
    sensors: list = BlockInput()

    def validate(self, sensor):
        template = sensor.ERROR_TEMPLATE

        value = self.setup.log_reader.search(template)
        self.assertIsNotNone(value, f"Couldnt find {sensor} log line")

    def test_method(self):
        for sensor, expected_value in self.expected_values.items():
            if sensor.check_error(expected_value):
                self.validate(sensor)
