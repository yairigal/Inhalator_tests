from itertools import product

from rotest.core.flow import TestFlow
from rotest.core.flow_component import MODE_FINALLY

from air_to_breath.blocks.blocks import SetSensorsValues
from air_to_breath.blocks.blocks import StartProgram
from air_to_breath.blocks.blocks import ClearBuffer
from air_to_breath.blocks.blocks import ValidateSensors
from air_to_breath.blocks.blocks import StopProgram
from air_to_breath.tests.common import SENSORS
from air_to_breath_resources.resources import AirToBreathSetup


class AbstractSanityFlow(TestFlow):
    __test__ = False

    blocks = [
        StartProgram,

        ClearBuffer,
        SetSensorsValues,
        ValidateSensors,
        # ValidateSensorsError,

        # Teardown
        StopProgram.params(mode=MODE_FINALLY)
    ]


def create_scenarios():
    scenarios = []
    for sensor_name, sensor_obj in SENSORS.items():
        low_bound = sensor_obj.low_bound - 1
        high_bound = sensor_obj.high_bound + 1
        legal = (low_bound + high_bound) / 2.0
        scenarios.append([(sensor_name, legal), (sensor_name, low_bound), (sensor_name, high_bound)])

    yield from product(*scenarios)


class SanityFlow(TestFlow):
    setup = AirToBreathSetup.request()

    blocks = [
        AbstractSanityFlow.params(name=f'{s1}_{s2}: {s1_value} {s2_value}',
                                  sensors=[s1, s2],
                                  sent_values=[s1_value, s2_value])
        for (s1, s1_value), (s2, s2_value) in create_scenarios()
    ]
