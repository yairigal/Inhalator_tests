from rotest.core.flow import TestFlow
from rotest.core.flow_component import MODE_FINALLY

from air_to_breath.blocks.blocks import ClearBuffer, ValidateSensors, \
    StartSensorSimulation, StopSensorSimulation
from air_to_breath_resources.resources import AirToBreathSetup


class AbstractSensorFlow(TestFlow):
    __test__ = False

    blocks = [ClearBuffer,
              StartSensorSimulation,
              ValidateSensors,
              StopSensorSimulation.params(mode=MODE_FINALLY)]


class SanityFlow(TestFlow):
    setup = AirToBreathSetup.request()

    common = {'sent_values': [3]}

    blocks = [AbstractSensorFlow.params(sensors=[setup.pressure]),
              AbstractSensorFlow.params(sensors=[setup.flow]),
              AbstractSensorFlow.params(sensors=[setup.oxygen])]


class UpperBoundFlow(TestFlow):
    setup = AirToBreathSetup.request()

    common = {'sent_values': [7]}

    blocks = [AbstractSensorFlow.params(sensors=[setup.pressure]),
              AbstractSensorFlow.params(sensors=[setup.flow]),
              AbstractSensorFlow.params(sensors=[setup.oxygen])]


class LowBoundFlow(TestFlow):
    setup = AirToBreathSetup.request()

    common = {'sent_values': [-3]}

    blocks = [AbstractSensorFlow.params(sensors=[setup.pressure]),
              AbstractSensorFlow.params(sensors=[setup.flow]),
              AbstractSensorFlow.params(sensors=[setup.oxygen])]