from time import localtime

from fan import Fan
from measurements import Measurements


class FanCondition:
    def __init__(self, fan: Fan, measurements: Measurements):
        self.fan = fan
        self.measurements = measurements

    def __call__(self):
        retval = self.handle()
        # clasname=self.__class__.__name__
        # print(f'{clasname}(C) -> {retval}')
        return retval

    def __bool__(self):
        retval = self.handle()
        # clasname = self.__class__.__name__
        # print(f'{clasname}(B) -> {retval}')
        return retval

    def handle(self):
        pass

    def take_action(self):
        pass

    @staticmethod
    def min_on_time():
        current_time = localtime()

        if current_time.tm_wday in (5, 6):  # weekend
            if current_time.tm_hour in (list(range(0, 6)) + list(range(23, 24))):
                return 5 * 60

        return 15 * 60

    @staticmethod
    def max_on_time():
        current_time = localtime()

        if current_time.tm_wday in (5, 6):  # weekend
            if current_time.tm_hour in (list(range(0, 6)) + list(range(23, 24))):
                return 15 * 60

        return 60 * 60


class FanStopCond(FanCondition):
    def take_action(self):
        self.fan.off()


class FanStartCond(FanCondition):
    def take_action(self):
        self.fan.on()


class HighHumidityAndHighSlopeCondtion(FanStartCond):
    def handle(self):
        humidity, slope = self.measurements.humidity, self.measurements.slope
        if humidity >= 80 and slope >= 1:
            self.take_action()
            return True
        return False


class LowHumiditySmallSlopeCondition(FanStopCond):
    def handle(self):
        humidity, slope = self.measurements.humidity, self.measurements.slope
        if humidity < 80 and slope > -0.25 and self.fan.on_time() > self.min_on_time():
            self.take_action()
            return True
        return False


class LongRunningTimeCondition(FanStopCond):
    def handle(self):
        if self.fan.on_time() > self.max_on_time():
            self.take_action()
            return True
        return False
