import logging
import os
from inspect import isabstract

from conditions import FanStopCondition, FanStartCondition
from fan import TimedFan
from measurements import Measurements

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class FanController:
    def __init__(self, fan: TimedFan, measurements: Measurements):
        self.fan = fan
        self.measurements = measurements

        import conditions

        constraint = lambda x: issubclass(x, (FanStartCondition, FanStopCondition)) and not isabstract(x)
        sort_key = lambda x: issubclass(x, FanStopCondition)

        _conditions = filter(lambda x: 'Condition' in x, dir(conditions))
        _conditions = map(lambda x: 'conditions.{:s}'.format(x), _conditions)
        _conditions = map(eval, _conditions)
        _conditions = sorted(filter(constraint, _conditions), key=sort_key)  # start conditions first
        self.conditions = list(map(lambda x: x(fan, measurements), _conditions))

    def do_stuff(self):
        if not os.path.exists('/tmp/bypass'):
            any(self.conditions)
        else:
            log.info('Bypass /tmp/bypass')

    def __call__(self, *args, **kwargs):
        return self.do_stuff()
