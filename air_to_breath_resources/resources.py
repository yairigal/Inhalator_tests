"""All air_to_breath2 project resources."""
import time
from pathlib import Path

from rotest.management.base_resource import BaseResource

from air_to_breath_resources.utils.log_parser import LogReader
from air_to_breath_resources.utils.sensor import FlowSensor
from air_to_breath_resources.utils.sensor import OxygenSensor
from air_to_breath_resources.utils.sensor import PressureSensor
from air_to_breath_resources.utils.ssh import SSH


class AirToBreathSetup(BaseResource):
    RPI_IP = "169.254.163.124"

    RP_USER = 'pi'
    RP_PASSWORD = 'raspberry'

    REPO = Path('/home/pi/Inhalator')
    START_CMD = 'export DISPLAY=:0 && python3 /home/pi/Inhalator/main.py -vvv &> /tmp/atb_log'
    STOP_CMD = 'pkill -f python3'

    REMOTE_DRIVERS_PATH = REPO / 'drivers' / 'mocks'
    REMOTE_PRESSURE_DRIVER = REMOTE_DRIVERS_PATH / 'mock_hce_pressure_sensor.py'
    REMOTE_FLOW_DRIVER = REMOTE_DRIVERS_PATH / 'mock_sfm3200_flow_sensor.py'
    REMOTE_OXYGEN_DRIVER = ''  # TODO need to add when they are done

    OLD_PRESSURE_NAME = REMOTE_DRIVERS_PATH / 'pressure_old'
    OLD_FLOW_NAME = REMOTE_DRIVERS_PATH / 'flow_old'
    OLD_OXYGEN_NAME = REMOTE_DRIVERS_PATH / 'oxygen_old'

    THIS_FILE = Path(__file__)
    LOCAL_DRIVERS = THIS_FILE.parent / 'remote_drivers'
    LOCAL_PRESSURE_DRIVER = LOCAL_DRIVERS / 'pressure_sensor.py'
    LOCAL_FLOW_DRIVER = LOCAL_DRIVERS / 'flow_sensor.py'
    LOCAL_OXYGEN_DRIVER = LOCAL_DRIVERS / 'oxygen_sensor.py'

    PRESSURE_PORT = 5555
    FLOW_PORT = 6666
    OXYGEN_PORT = 7777

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log_reader = LogReader()

        self.pressure = PressureSensor(self.RPI_IP, self.PRESSURE_PORT)
        self.flow = FlowSensor(self.RPI_IP, self.FLOW_PORT)
        self.oxygen = OxygenSensor(self.RPI_IP, self.OXYGEN_PORT)

        self.logger.info('Connecting to RP through SSH')
        self.ssh = SSH(self.RPI_IP, self.RP_USER, self.RP_PASSWORD)

    def copy_pressure(self):
        # rename old_drivers
        self.ssh.execute(f'mv {self.REMOTE_PRESSURE_DRIVER} {self.OLD_PRESSURE_NAME}')
        # copy new drivers with old drivers name
        self.ssh.copy(str(self.LOCAL_PRESSURE_DRIVER), str(self.REMOTE_PRESSURE_DRIVER))

    def copy_flow(self):
        # rename old_drivers
        self.ssh.execute(f'mv {self.REMOTE_FLOW_DRIVER} {self.OLD_FLOW_NAME}')
        # copy new drivers with old drivers name
        self.ssh.copy(str(self.LOCAL_FLOW_DRIVER), str(self.REMOTE_FLOW_DRIVER))

    def copy_oxygen(self):
        # rename old_drivers
        self.ssh.execute(f'mv {self.REMOTE_OXYGEN_DRIVER} {self.OLD_OXYGEN_NAME}')
        # copy new drivers with old drivers name
        self.ssh.copy(str(self.LOCAL_OXYGEN_DRIVER), str(self.REMOTE_OXYGEN_DRIVER))

    def _copy_drivers_to_remote(self):
        self.logger.debug('copying new drivers to remote')
        # rename old_drivers
        self.copy_pressure()
        self.copy_flow()
        # TODO add copy of oxygen sensor
        # self.copy_oxygen()

    def _recover_drivers(self):
        self.logger.debug("recovering drivers")
        self.ssh.execute(f'mv {self.OLD_PRESSURE_NAME} {self.REMOTE_PRESSURE_DRIVER}')
        self.ssh.execute(f'mv {self.OLD_FLOW_NAME} {self.REMOTE_FLOW_DRIVER}')

    def connect(self):
        self.logger.debug("Starting log reader")
        self.log_reader.start_logger()
        self._copy_drivers_to_remote()

        self.logger.info("Starting program")
        self.start_program()

    def start_program(self):
        out, err = self.ssh.execute(self.START_CMD, wait=False)
        # TODO add wait here
        time.sleep(5)
        return out, err

    def stop_program(self):
        return self.ssh.execute(self.STOP_CMD, wait=False)

    def finalize(self):
        self.logger.info("stopping program")
        self.stop_program()

        self._recover_drivers()

        self.logger.debug("Stopping log reader")
        self.log_reader.stop()
