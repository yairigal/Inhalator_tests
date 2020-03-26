import re


def validate_alarm(mock):  # get rid of mock
    return mock  # TODO CHECK ALARM HAPPENED


class BaseValidator:
    LOG_WAIT_SECONDS = 3

    SENSOR_LINE = NotImplemented
    WARNING_LINE = "WRONG_LINE"  # TODO CHANGE THIS
    VALUE_REGEX = "\w+: (.*)"  # TODO CHANGE THIS

    @classmethod
    def get_value(cls, log_line, regex):
        res = re.search(cls.VALUE_REGEX, log_line)
        if res is None:
            raise RuntimeError('ERROR')

        return float(res.group(1))

    @classmethod
    def validate(cls, expected_value, low_bound, high_bound, log_reader):
        if expected_value < low_bound or expected_value > high_bound:
            expected_log = cls.WARNING_LINE
            alarm = True

        else:
            expected_log = cls.SENSOR_LINE
            alarm = False

        found = log_reader.wait_for_log(expected_log,
                                        timeout=cls.LOG_WAIT_SECONDS)
        if not found:
            return False, f"Pressure log '{expected_log}' was not found"

        # log_line = log_reader.search(expected_log)
        # import ipdb;ipdb.set_trace(context=20)
        # value = cls.get_value(log_line)
        value = float(log_reader.search(expected_log))

        if float(value) != expected_value:
            return False, f"Expected pressure value {expected_value}," \
                f"got {value}"

        beeped = validate_alarm(alarm)
        if alarm and not beeped:
            return False, "Alarm didn't beeped when it should"

        if not alarm and beeped:
            return False, "Alarm beeped when it shouldn't"

        return True, ""


class PressureValidator(BaseValidator):
    SENSOR_LINE = "Pressure: (.*)"


class FlowValidator(BaseValidator):
    SENSOR_LINE = "Flow: (.*)"


class OxygenValidator(BaseValidator):
    SENSOR_LINE = "WRONG_LINE"  # TODO CHANGE THIS
