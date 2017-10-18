import logging
from time import localtime

from fan import TimedFan
from measurements import Measurements
from util import isQuietTime

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FanCondition:
    def __init__(self, fan: TimedFan, measurements: Measurements):
        self.fan = fan
        self.measurements = measurements

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
        current_time = localtime()
        if isQuietTime(current_time):
            return 5 * 60
        return 15 * 60

    @staticmethod
    def max_on_time():
        current_time = localtime()
        if isQuietTime(current_time):
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


from conditions.force_conditions import ForceStartCondition, ForceStopCondition
from conditions.high_humidity_high_slope_condition import HighHumidityAndHighSlopeCondition
from conditions.long_running_time_condition import LongRunningTimeCondition
from conditions.low_humidity_small_slope_condition import LowHumiditySmallSlopeCondition
