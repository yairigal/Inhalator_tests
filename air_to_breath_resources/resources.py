"""All air_to_breath2 project resources."""
import json
import os
from pathlib import Path

import waiting
from rotest.management.base_resource import BaseResource

from air_to_breath.tests.common import SENSORS
from air_to_breath_resources.utils.log_parser import LogReader
from air_to_breath_resources.utils.ssh import SSH


class AirToBreathSetup(BaseResource):
    RP_USER = 'pi'
    RP_PASSWORD = 'raspberry'

    REPO = Path('/home/pi/Inhalator')
    REMOTE_DRIVERS_PATH = REPO / 'drivers'

    LOG_FILE_PATH = Path('/tmp/atb_log')
    CMD_LABEL = f'python3 {REPO}/main.py -vvv'
    START_CMD = f'export DISPLAY=:0 && {CMD_LABEL} &> {LOG_FILE_PATH} &'
    STOP_CMD = 'pkill -f python3'

    REMOTE_PRESSURE_DRIVER = REMOTE_DRIVERS_PATH / 'hce_pressure_sensor.py'
    REMOTE_FLOW_DRIVER = REMOTE_DRIVERS_PATH / 'sfm3200_flow_sensor.py'
    REMOTE_OXYGEN_DRIVER = REMOTE_DRIVERS_PATH / ''  # TODO need to add when they are done

    OLD_PRESSURE_NAME = REMOTE_DRIVERS_PATH / 'pressure_old'
    OLD_FLOW_NAME = REMOTE_DRIVERS_PATH / 'flow_old'
    OLD_OXYGEN_NAME = REMOTE_DRIVERS_PATH / 'oxygen_old'

    THIS_FILE = Path(__file__)
    LOCAL_DRIVERS = THIS_FILE.parent / 'remote_drivers'
    LOCAL_PRESSURE_DRIVER = LOCAL_DRIVERS / 'pressure_sensor.py'
    LOCAL_FLOW_DRIVER = LOCAL_DRIVERS / 'flow_sensor.py'
    LOCAL_OXYGEN_DRIVER = LOCAL_DRIVERS / 'oxygen_sensor.py'

    OLD_CONFIG_FILE = REPO / 'old_config'
    REMOTE_CONFIG_FILE = REPO / 'config.json'

    SENSOR_TO_PORT = {
        'pressure': 5555,
        'flow': 6666,
        'oxygen': 7778
    }

    def __init__(self, host=None, **kwargs):
        super().__init__(**kwargs)
        self.host = host if host is not None else self.config['ip']
        self.log_reader = LogReader(self.config['debug_port'])

        self.logger.info('Connecting to RP through SSH')
        self.ssh = SSH(self.host, self.RP_USER, self.RP_PASSWORD)

    def set_value(self, sensor, value):
        SENSORS[sensor].set_value(value, self.host, self.SENSOR_TO_PORT[sensor])
        return value

    def recover_config(self):
        self.ssh.execute(f'mv {self.OLD_CONFIG_FILE} {self.REMOTE_CONFIG_FILE}')
        self.ssh.execute(f'rm {self.OLD_CONFIG_FILE}')

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
        self.copy_pressure()
        self.copy_flow()
        # TODO add copy of oxygen sensor
        # self.copy_oxygen()

    def _recover_drivers(self):
        self.logger.debug("recovering drivers")
        self.recover_config()
        # pressure
        self.ssh.execute(f'mv {self.OLD_PRESSURE_NAME} {self.REMOTE_PRESSURE_DRIVER}')
        self.ssh.execute(f'rm {self.OLD_PRESSURE_NAME}')
        # flow
        self.ssh.execute(f'mv {self.OLD_FLOW_NAME} {self.REMOTE_FLOW_DRIVER}')
        self.ssh.execute(f'rm {self.OLD_FLOW_NAME}')

    def connect(self):
        self.logger.debug("Starting log reader")
        self.log_reader.start_logger()

    def is_online(self):
        out, err = self.ssh.execute('ps aux -T | '  # show all process and threads
                                    'grep -v grep | '  # remove grep cmds
                                    'grep -v bash | '  # remove the ssh complex cmd
                                    f'grep "{self.CMD_LABEL}" | '  # search for the specific process
                                    f'wc -l')  # count instances
        return int(out.decode().strip()) == 3  # all threads are up

    def _copy_config(self):
        self.ssh.execute(f'mv {self.REMOTE_CONFIG_FILE} {self.OLD_CONFIG_FILE}')
        tmp_file = Path(__file__).parent / 'tmp_config.json'
        with open(tmp_file, 'w') as f:
            json.dump(dict(self.config), f, indent=4)

        self.ssh.copy(str(tmp_file), str(self.REMOTE_CONFIG_FILE))

        os.system(f'rm {tmp_file}')

    def start_program(self):
        self._copy_config()
        self._copy_drivers_to_remote()

        self.logger.info("Starting program")
        out, err = self.ssh.execute(self.START_CMD, wait=False)
        waiting.wait(self.is_online, timeout_seconds=10, sleep_seconds=1)
        return out, err

    def stop_program(self):
        self.logger.info("stopping program")
        self.ssh.execute(self.STOP_CMD)
        waiting.wait(lambda: not self.is_online())

        self._recover_drivers()

    def finalize(self):
        self.logger.debug("Stopping log reader")
        self.log_reader.stop()
