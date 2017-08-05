from abc import abstractmethod

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

    @abstractmethod
    def handle(self):
        pass

    @abstractmethod
    def take_action(self):
        pass


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
        if humidity < 80 and slope > -0.25:  # and fan.on_time() > (15*60):
            self.take_action()
            return True
        return False


class LongRunningTimeCondition(FanStopCond):
    def handle(self):
        if self.fan.on_time() > self.maxontime():
            self.take_action()
            return True
        return False

    def maxontime(self):
        # TODO: make it time dependant
        return 15 * 60
