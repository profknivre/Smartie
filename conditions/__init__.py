import logging
from abc import ABC, abstractmethod
from inspect import isabstract
from time import localtime

import config
from util import isQuietTime

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FanCondition(ABC):
    def __init__(self, fan, measurements):
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

    @abstractmethod
    def handle(self):
        pass # pragma: nocover

    @abstractmethod
    def take_action(self):
        pass # pragma: nocover

    @staticmethod
    def min_on_time():
        current_time = localtime()
        if isQuietTime(current_time):
            return config.fan_runtime_min_quiet
        return config.fan_runtime_min

    @staticmethod
    def max_on_time():
        current_time = localtime()
        if isQuietTime(current_time):
            return config.fan_runtime_max_quiet
        return config.fan_runtime_max


class FanStopCondition(FanCondition):
    def take_action(self):
        if self.fan.is_on():
            self.fan.off(str(self))


class FanStartCondition(FanCondition):
    def take_action(self):
        if not self.fan.is_on():
            self.fan.on(str(self))


from .low_humidity_small_slope_condition import *
from .long_running_time_condition import *
from .high_humidity_high_slope_condition import *
from .force_conditions import *

def get_condition_list():
    stop_conds = FanStopCondition.__subclasses__()
    start_conds = FanStartCondition.__subclasses__()

    condition_classes = stop_conds + start_conds
    condition_classes = filter(lambda x: not isabstract(x), condition_classes)
    return condition_classes
