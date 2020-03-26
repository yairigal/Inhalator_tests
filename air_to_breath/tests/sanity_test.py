import re

from rotest.core.case import TestCase

from air_to_breath_resources.resources import AirToBreathSetup


class PressureSanityTest(TestCase):
    LOG_WAIT_SECONDS = 3

    PRESSURE_LINE = 'WRONG_LINE'  # TODO CHANGE THIS

    setup = AirToBreathSetup.request()

    def test_sanity(self):
        self.setup.log_reader.clear_buffer()

        with self.setup.pressure.simulate():
            value = self.setup.log_reader.wait_for_log(self.PRESSURE_LINE, timeout=self.LOG_WAIT_SECONDS)
            match = re.search(self.PRESSURE_LINE, value).group(1)
            self.assertTrue(int(match))

            self.assertIsNotNone(value)


class FlowSanityTest(TestCase):
    LOG_WAIT_SECONDS = 3

    START_FLOW_LOG = 'WRONG_LINE'  # TODO CHANGE THIS
    STOP_FLOW_LOG = 'WRONG_LINE'  # TODO CHANGE THIS

    setup = AirToBreathSetup.request()

    def test_sanity(self):
        self.setup.log_reader.clear_buffer()

        with self.setup.flow.simulate():
            self.assertIsNotNone(self.setup.log_reader.wait_for_log(self.START_FLOW_LOG,
                                                                    timeout=self.LOG_WAIT_SECONDS))
            self.assertIsNotNone(self.setup.log_reader.wait_for_log(self.STOP_FLOW_LOG,
                                                                    timeout=self.LOG_WAIT_SECONDS))


class OxygenSanityTest(TestCase):
    LOG_WAIT_SECONDS = 3

    START_FLOW_LOG = 'WRONG_LINE'  # TODO CHANGE THIS
    STOP_FLOW_LOG = 'WRONG_LINE'  # TODO CHANGE THIS

    setup = AirToBreathSetup.request()

    def test_sanity(self):
        self.setup.log_reader.clear_buffer()

        with self.setup.oxygen.simulate():
            self.assertIsNotNone(self.setup.log_reader.wait_for_log(self.START_FLOW_LOG,
                                                                    timeout=self.LOG_WAIT_SECONDS))
            self.assertIsNotNone(self.setup.log_reader.wait_for_log(self.STOP_FLOW_LOG,
                                                                    timeout=self.LOG_WAIT_SECONDS))

