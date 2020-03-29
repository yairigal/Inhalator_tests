from itertools import combinations

from rotest.core.flow import TestFlow
from rotest.core.flow_component import MODE_FINALLY

from air_to_breath.blocks.blocks import ClearBuffer
from air_to_breath.blocks.blocks import InitializeSensorValuesBlock
from air_to_breath.blocks.blocks import SetSensorsValues
from air_to_breath.blocks.blocks import StartProgram
from air_to_breath.blocks.blocks import StopProgram
from air_to_breath.blocks.blocks import ValidateSensors
from air_to_breath.tests.common import SENSORS
from air_to_breath_resources.resources import AirToBreathSetup


class AbstractSanityFlow(TestFlow):
    __test__ = False

    setup = AirToBreathSetup.request()

    blocks = [
        InitializeSensorValuesBlock,
        StartProgram,

        ClearBuffer,
        SetSensorsValues,
        ValidateSensors,

        StopProgram.params(mode=MODE_FINALLY)
    ]


class SanityFlow(TestFlow):
    setup = AirToBreathSetup.request()

    blocks = [
        AbstractSanityFlow.params(sensors=['pressure']),
        AbstractSanityFlow.params(sensors=['flow']),
        # AbstractSensorFlow.params(sensors=[setup.oxygen])
    ]


class UpperBoundFlow(TestFlow):
    setup = AirToBreathSetup.request()

    common = {'sent_values': [7]}

    blocks = [
        AbstractSanityFlow.params(sensors=['pressure']),
        AbstractSanityFlow.params(sensors=['flow']),
        # AbstractSensorFlow.params(sensors=[setup.oxygen])
    ]


class LowBoundFlow(TestFlow):
    setup = AirToBreathSetup.request()

    common = {'sent_values': [-3]}

    blocks = [
        AbstractSanityFlow.params(sensors=['pressure']),
        AbstractSanityFlow.params(sensors=['flow']),
        # AbstractSensorFlow.params(sensors=[setup.oxygen])
    ]


class PairsSanityFlow(TestFlow):
    setup = AirToBreathSetup.request()

    blocks = [AbstractSanityFlow.params(sensors=[s1, s2]) for s1, s2 in combinations(SENSORS, 2)]


class TripletsSanityFlow(TestFlow):
    setup = AirToBreathSetup.request()

    blocks = [AbstractSanityFlow.params(sensors=[s1, s2, s3]) for s1, s2, s3 in combinations(SENSORS, 3)]
