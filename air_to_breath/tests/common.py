from air_to_breath_resources.utils.sensor import FlowSensor
from air_to_breath_resources.utils.sensor import PressureSensor

SENSORS = {
    'pressure': PressureSensor(),
    'flow': FlowSensor(),
    # 'oxygen': OxygenSensor
}
