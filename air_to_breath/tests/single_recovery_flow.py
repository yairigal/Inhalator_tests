from rotest.core.flow import TestFlow
from rotest.core.flow_component import MODE_FINALLY

from air_to_breath2.blocks.blocks import ClearBuffer, ValidateSensors, \
    StartSensorSimulation, StopSensorSimulation, UpperCrossSensorValue, \
    NormalizeSensorValue, LowerCrossSensorValue
from air_to_breath_resources.resources import AirToBreathSetup


class AbstractUpperRecoverySensorFlow(TestFlow):
    __test__ = False

    blocks = [ClearBuffer,
              StartSensorSimulation,
              ValidateSensors,
              UpperCrossSensorValue,
              ValidateSensors,
              NormalizeSensorValue,
              ValidateSensors,
              StopSensorSimulation.params(mode=MODE_FINALLY)]


class AbstractLowerRecoverySensorFlow(TestFlow):
    __test__ = False

    blocks = [ClearBuffer,
              StartSensorSimulation,
              ValidateSensors,
              LowerCrossSensorValue,
              ValidateSensors,
              NormalizeSensorValue,
              ValidateSensors,
              StopSensorSimulation.params(mode=MODE_FINALLY)]


class UpperRecoveryFlow(TestFlow):
    setup = AirToBreathSetup.request()

    blocks = [AbstractUpperRecoverySensorFlow.params(sensors=[sensor])
              for sensor in [setup.pressure, setup.flow, setup.oxygen]]


class LowerRecoveryFlow(TestFlow):
    setup = AirToBreathSetup.request()

    blocks = [AbstractLowerRecoverySensorFlow.params(sensors=[sensor])
              for sensor in [setup.pressure, setup.flow, setup.oxygen]]
