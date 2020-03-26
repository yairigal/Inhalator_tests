from rotest.core.block import TestBlock
from rotest.core.flow_component import BlockInput, BlockOutput

from air_to_breath_resources.utils.sensor import PressureSensor, FlowSensor, OxygenSensor
from air_to_breath_resources.utils.Validator import PressureValidator, FlowValidator, OxygenValidator

SENSOR_TO_VALIDATE = {PressureSensor: PressureValidator,
                      FlowSensor: FlowValidator,
                      OxygenSensor: OxygenValidator}


class ClearBuffer(TestBlock):
    setup = BlockInput()

    def test_method(self):
        self.setup.log_reader.clear_buffer()


class StartSensorSimulation(TestBlock):
    sensors = BlockInput()
    sent_values = BlockInput(default=None)
    low_values = BlockInput(default=None)
    high_values = BlockInput(default=None)

    expected_values = BlockOutput()

    def test_method(self):
        self.expected_values = {}
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
            sensor.change_sensor_value(sensor_value)
            self.expected_values[sensor] = sensor


class UpperCrossSensorValue(TestBlock):
    sensors = BlockInput()
    expected_values = BlockInput()

    def test_method(self):
        for sensor in self.sensors:
            new_value = sensor.high_bound + 1
            self.expected_values[sensor] = new_value
            sensor.change_sensor_value(new_value)


class LowerCrossSensorValue(TestBlock):
    sensors = BlockInput()
    expected_values = BlockInput()

    def test_method(self):
        for sensor in self.sensors:
            new_value = sensor.low_bound - 1
            self.expected_values[sensor] = new_value
            sensor.change_sensor_value(new_value)


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
    setup = BlockInput()
    sensors = BlockInput()
    expected_values = BlockInput()

    def test_method(self):
        for sensor, expected_value in zip(self.sensors, self.expected_values):
            validator = SENSOR_TO_VALIDATE[sensor]
            expected_value = self.expected_values[sensor]
            valid, error = validator.validate(expected_value,
                                              sensor.low_bound,
                                              sensor.high_bound,
                                              self.setup.log_reader)

            self.assertTrue(valid, error)


