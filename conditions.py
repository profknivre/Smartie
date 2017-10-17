import logging
import os
from time import localtime

from fan import TimedFan
from measurements import Measurements

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FanCondition:
    def __init__(self, fan: TimedFan, measurements: Measurements):
        self.fan = fan
        self.measurements = measurements

    def __call__(self):
        retval = self.handle()
        log.debug('{}(C) -> {}'.format(self.__class__.__name__, retval))
        return retval

    def __bool__(self):
        retval = self.handle()
        # clasname = self.__class__.__name__
        # print(f'{clasname}(B) -> {retval}')
        log.debug('{}(B) -> {}'.format(self.__class__.__name__, retval))
        return retval

    def __str__(self) -> str:
        return str(self.__class__.__name__)

    def handle(self):
        pass

    def take_action(self):
        pass

    @staticmethod
    def min_on_time():
        """
        :return: minimum running time depending on weekday and hour
        """
        current_time = localtime()

        if current_time.tm_wday in (5, 6):  # weekend
            if current_time.tm_hour in (list(range(0, 6)) + list(range(23, 24))):
                return 5 * 60

        return 15 * 60

    @staticmethod
    def max_on_time():
        """
        :return: maximum running time depending on weekday and hour
        """
        current_time = localtime()

        if current_time.tm_wday in (5, 6):  # weekend
            if current_time.tm_hour in (list(range(0, 6)) + list(range(23, 24))):
                return 15 * 60

        return 60 * 60


class FanStopCond(FanCondition):
    def take_action(self):
        if self.fan.is_on():
            self.fan.off(str(self))


class FanStartCond(FanCondition):
    def take_action(self):
        if not self.fan.is_on():
            self.fan.on(str(self))


class HighHumidityAndHighSlopeCondition(FanStartCond):
    """
    if humidity >= 80 and slope >= 1:
    """
    def handle(self):
        humidity, slope = self.measurements.bathroom_humidity, self.measurements.bathroom_humidity_slope
        if humidity >= 80 and slope >= 1:
            self.take_action()
            return True
        return False


class LowHumiditySmallSlopeCondition(FanStopCond):
    """
    if humidity < 80 and slope > -0.25 and self.fan.on_time() > self.min_on_time()
    """
    def handle(self):
        humidity, slope = self.measurements.bathroom_humidity, self.measurements.bathroom_humidity_slope
        if humidity < 80 and slope > -0.25 and self.fan.on_time() > self.min_on_time():
            self.take_action()
            return True
        return False


class LongRunningTimeCondition(FanStopCond):
    """
    if self.fan.on_time() > self.max_on_time():
    """
    def handle(self):
        if self.fan.on_time() > self.max_on_time():
            self.take_action()
            return True
        return False


FORCEFANSTOP = '/tmp/forcefanstop'
FORCEFANSTART = '/tmp/forcefanstart'


class ForceStartCondition(FanStartCond):
    def handle(self):
        if os.path.exists(FORCEFANSTART):
            os.unlink(FORCEFANSTART)
            self.take_action()
            return True
        return False


class ForceStopCondition(FanStopCond):
    def handle(self):
        if os.path.exists(FORCEFANSTOP):
            os.unlink(FORCEFANSTOP)
            self.take_action()
            return True
        return False
