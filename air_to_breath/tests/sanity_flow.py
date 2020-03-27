from itertools import product

from rotest.core.flow import TestFlow
from rotest.core.flow_component import MODE_FINALLY

from air_to_breath.blocks.blocks import StartProgram, ClearBuffer, \
    ValidateSensors, ValidateSensorsError, StopProgram
from air_to_breath_resources.resources import AirToBreathSetup


class AbstractSanityFlow(TestFlow):
    __test__ = False

    blocks = [StartProgram,
              ClearBuffer,
              ValidateSensors,
              ValidateSensorsError,
              StopProgram.params(mode=MODE_FINALLY)]


def create_scenarios(setup):
    sensors = [setup.pressure, setup.flow, setup.oxygen]
    scenarios = []
    for sensor in sensors:
        low_bound = sensor.low_bound - 1
        high_bound = sensor.high_bound + 1
        legal = (sensor.low_bound + sensor.high_bound) / 2.0
        scenarios.append([(sensor, legal), (sensor, low_bound), (sensor, high_bound)])

    for scenario in product(*scenarios):
        yield scenario


class SanityFlow(TestFlow):
    setup = AirToBreathSetup.request()

    blocks = [AbstractSanityFlow.params(sensors=[s1[0], s2[0], s3[0]],
                                        sent_values=[s1[1], s2[1], s3[1]])
              for s1, s2, s3 in create_scenarios(setup)]