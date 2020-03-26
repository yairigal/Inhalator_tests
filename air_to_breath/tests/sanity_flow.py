from rotest.core.flow import TestFlow
from rotest.core.flow_component import Pipe

from air_to_breath.blocks.blocks import ClearBuffer
from air_to_breath.blocks.blocks import InitializeSensorValuesBlock
from air_to_breath.blocks.blocks import ValidateSensors
from air_to_breath_resources.resources import AirToBreathSetup


class AbstractSensorFlow(TestFlow):
    __test__ = False

    blocks = [
        InitializeSensorValuesBlock,

        ClearBuffer,
        ValidateSensors
    ]


class SanityFlow(TestFlow):
    setup = AirToBreathSetup.request()

    blocks = [
        AbstractSensorFlow.params(sensors=Pipe('setup', lambda setup: [setup.pressure])),
        AbstractSensorFlow.params(sensors=Pipe('setup', lambda setup: [setup.flow])),
        # AbstractSensorFlow.params(sensors=[setup.oxygen])
    ]


class UpperBoundFlow(TestFlow):
    setup = AirToBreathSetup.request()

    common = {'sent_values': [7]}

    blocks = [
        AbstractSensorFlow.params(sensors=Pipe('setup', lambda setup: [setup.pressure])),
        AbstractSensorFlow.params(sensors=Pipe('setup', lambda setup: [setup.flow])),
        # AbstractSensorFlow.params(sensors=[setup.oxygen])
    ]


class LowBoundFlow(TestFlow):
    setup = AirToBreathSetup.request()

    common = {'sent_values': [-3]}

    blocks = [
        AbstractSensorFlow.params(sensors=Pipe('setup', lambda setup: [setup.pressure])),
        AbstractSensorFlow.params(sensors=Pipe('setup', lambda setup: [setup.flow])),
        # AbstractSensorFlow.params(sensors=[setup.oxygen])
    ]
