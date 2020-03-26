from itertools import product, combinations

from rotest.core.flow import TestFlow, create_flow
from rotest.core.flow_component import MODE_FINALLY, MODE_OPTIONAL

from air_to_breath.blocks.blocks import ClearBuffer, ValidateSensors, \
    StartSensorSimulation, StopSensorSimulation, UpperCrossSensorValue, \
    NormalizeSensorValue, LowerCrossSensorValue
from air_to_breath_resources.resources import AirToBreathSetup


def get_all_scenarios(sensors):
    sensor1, sensor2, sensor3 = sensors
    states = [UpperCrossSensorValue, LowerCrossSensorValue, NormalizeSensorValue]
    scenarios = []
    for state1, state2, state3 in product(states, states):
        scenarios += [state1.params(sensors=[sensor1]),
                      state2.params(sensors=[sensor2]),
                      state3.params(sensors=[sensor3])]
        scenarios += [ValidateSensors, NormalizeSensorValue, ValidateSensors]

    return scenarios


class CoupleRecoveryFlow2(TestFlow):
    setup = AirToBreathSetup.request()

    blocks = [create_flow(name=f"{s1}, {s2}, {s3} combinations",
                          common={'sensors': [s1, s2, s3]},
                          mode=MODE_OPTIONAL,
                          blocks=[ClearBuffer,
                                  StartSensorSimulation,
                                  ValidateSensors] +
                                  get_all_scenarios([s1, s2, s3]) +
                                  [StopSensorSimulation.params(mode=MODE_FINALLY)])
              for s1, s2, s3 in combinations([setup.pressure, setup.flow, setup.oxygen], 3)]
