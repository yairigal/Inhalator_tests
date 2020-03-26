from itertools import combinations, product

from rotest.core.flow import TestFlow
from rotest.core.flow_component import MODE_FINALLY

from air_to_breath.blocks.blocks import ClearBuffer, ValidateSensors, \
    StartSensorSimulation, StopSensorSimulation
from air_to_breath_resources.resources import AirToBreathSetup


class AbstractCoupleSensorFlow(TestFlow):
    __test__ = False

    blocks = [ClearBuffer,
              StartSensorSimulation,
              ValidateSensors,
              StopSensorSimulation.params(mode=MODE_FINALLY)]


def create_scenarios(setup):
    sensors = [setup.pressure, setup.flow, setup.oxygen]
    scenarios = []
    for sensor in sensors:
        low_bound = sensor.low_bound - 1
        high_bound = sensor.high_bound + 1
        legal = (sensor.low_bound + sensor.high_bound) / 2.0
        scenarios.append([(sensor, legal), (sensor, low_bound), (sensor, high_bound)])

    for comb in combinations(scenarios, 2):
        for scenario in product(*comb):
            yield scenario


class SanityFlow(TestFlow):
    setup = AirToBreathSetup.request()

    blocks = [AbstractCoupleSensorFlow.params(sensors=[s1, s2],
                                              sent_values=[s1[1], s2[1]])
              for s1, s2 in create_scenarios(setup)]