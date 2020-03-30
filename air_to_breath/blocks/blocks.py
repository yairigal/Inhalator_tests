import time
from itertools import cycle

from rotest.core.block import TestBlock
from rotest.core.flow_component import BlockInput
from rotest.core.flow_component import BlockOutput

from air_to_breath.tests.common import SENSORS
from air_to_breath_resources.resources import AirToBreathSetup


class StartProgram(TestBlock):
    setup: AirToBreathSetup = BlockInput()
    sensors: list = BlockInput()

    expected_values = BlockOutput()

    def test_method(self):
        self.setup.start_program()
        self.expected_values = {}
        for sensor in self.sensors:
            value = self.setup.set_value(sensor, None)
            self.expected_values[sensor] = value


class StopProgram(TestBlock):
    setup: AirToBreathSetup = BlockInput()

    def test_method(self):
        self.setup.stop_program()


class ClearBuffer(TestBlock):
    setup: AirToBreathSetup = BlockInput()

    def test_method(self):
        self.setup.log_reader.clear_buffer()


class SetSensorsValues(TestBlock):
    sensors = BlockInput()
    expected_values: dict = BlockInput()
    setup: AirToBreathSetup = BlockInput()
    sent_values = BlockInput(default=cycle([None]))

    def test_method(self):
        # TODO add feature to send couple of values to a sensor (like a sin wave) to simulate real scenario.
        for sensor, sent_value in zip(self.sensors, self.sent_values):
            value = self.setup.set_value(sensor, sent_value)
            self.expected_values[sensor] = value

        time.sleep(0.5)  # Wait for program to sample


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
    expected_values: dict = BlockInput()

    def validate(self, sensor, expected_value):
        template = SENSORS[sensor].VALUE_TEMPLATE
        value = self.setup.log_reader.wait_for_log(template)
        self.assertIsNotNone(value, f"Couldnt find `{sensor}` log line")
        self.assertEqual(float(value), expected_value, f"got value={value}, expected={expected_value}")

    def test_method(self):
        for sensor, expected_value in self.expected_values.items():
            expected_value = self.expected_values[sensor]
            self.validate(sensor, expected_value)


class ValidateSensorsError(TestBlock):
    setup: AirToBreathSetup = BlockInput()
    expected_values: dict = BlockInput()

    CHECK_OPTIONS = [
        'LOW',
        'HIGH'
    ]

    def validate(self, sensor, expected_value, error_template):
        self.logger.info(f"Validating `{error_template}` occured in log")
        value = self.setup.log_reader.wait_for_log(error_template)
        self.assertEqual(float(value), expected_value, f"Couldnt find {sensor} error log line")

    def validate_no_errors(self, sensor):
        sensor_obj = SENSORS[sensor]
        for error_template in [sensor_obj.HIGH_ERROR_TEMPLATE, sensor_obj.LOW_ERROR_TEMPLATE]:
            self.assertIsNone(self.setup.log_reader.search(error_template), f"Found ERROR in log for {sensor}")

    def test_method(self):
        for sensor, expected_value in self.expected_values.items():
            sensor_obj = SENSORS[sensor]
            error_template_to_find = sensor_obj.is_exceeded(expected_value)
            if error_template_to_find is None:
                self.validate_no_errors(sensor)

            else:
                self.validate(sensor, expected_value, error_template=error_template_to_find)
