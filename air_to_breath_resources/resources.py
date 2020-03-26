"""All air_to_breath2 project resources."""
from pathlib import Path

from rotest.management.base_resource import BaseResource

from air_to_breath_resources.utils.log_parser import LogReader
from air_to_breath_resources.utils.sensor import SocketSensor
from air_to_breath_resources.utils.ssh import SSH


class AirToBreathSetup(BaseResource):
    RPI_IP = "169.254.163.124"

    RP_USER = 'pi'
    RP_PASSWORD = 'raspberry'

    REPO = Path('/home/pi/Inhalator')
    START_CMD = 'export DISPLAY=:0 && python3 /home/pi/Inhalator/main.py'
    STOP_CMD = 'pkill -f python3'

    REMOTE_DRIVERS_PATH = REPO / 'drivers'
    REMOTE_PRESSURE_DRIVER = REMOTE_DRIVERS_PATH / 'hce_pressure_sensor.py'
    REMOTE_FLOW_DRIVER = REMOTE_DRIVERS_PATH / 'sfm3200_flow_sensor.py'
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

        self.pressure = SocketSensor(self.RPI_IP, self.PRESSURE_PORT)
        self.flow = SocketSensor(self.RPI_IP, self.FLOW_PORT)
        self.oxygen = SocketSensor(self.RPI_IP, self.OXYGEN_PORT)

        self.logger.info('Connecting to RP through SSH')
        self.ssh = SSH(self.RPI_IP, self.RP_USER, self.RP_PASSWORD)

    def copy_driver(self):
        # rename old_drivers
        self.ssh.execute(f'mv {self.REMOTE_PRESSURE_DRIVER} {self.OLD_PRESSURE_NAME}')
        # copy new drivers with old drivers name
        self.ssh.copy(str(self.LOCAL_PRESSURE_DRIVER), str(self.REMOTE_PRESSURE_DRIVER))

    def _copy_drivers_to_remote(self):
        self.logger.debug('copying new drivers to remote')
        # rename old_drivers
        self.ssh.execute(f'mv {self.REMOTE_PRESSURE_DRIVER} {self.OLD_PRESSURE_NAME}')
        # copy new drivers with old drivers name
        self.ssh.copy(str(self.LOCAL_PRESSURE_DRIVER), str(self.REMOTE_PRESSURE_DRIVER))

        # rename old_drivers
        self.ssh.execute(f'mv {self.REMOTE_FLOW_DRIVER} {self.OLD_FLOW_NAME}')
        # copy new drivers with old drivers name
        self.ssh.copy(str(self.LOCAL_FLOW_DRIVER), str(self.REMOTE_FLOW_DRIVER))

        # TODO add copy of oxygen sensor

    def _recover_drivers(self):
        self.logger.debug("recovering drivers")
        self.ssh.execute(f'mv {self.OLD_PRESSURE_NAME} {self.REMOTE_PRESSURE_DRIVER}')

    def connect(self):
        self.logger.debug("Starting log reader")
        self.log_reader.start_logger()
        self._copy_drivers_to_remote()

    def start_program(self):
        return self.ssh.execute(self.START_CMD, wait=False)
        # TODO add wait here

    def stop_program(self):
        return self.ssh.execute(self.STOP_CMD, wait=False)

    def finalize(self):
        self._recover_drivers()

        self.logger.debug("Stopping log reader")
        self.log_reader.stop()
