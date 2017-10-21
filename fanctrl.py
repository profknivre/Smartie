import logging
import os

from conditions.condition_factory import ConditionFactory
from fan import TimedFan
from measurements import Measurements

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class FanController:
    def __init__(self, fan: TimedFan, measurements: Measurements):
        self.fan = fan
        self.measurements = measurements
        self.conditions = ConditionFactory(fan, measurements).build_all()

    def do_stuff(self):
        if not os.path.exists('/tmp/bypass'):
            any(self.conditions)
        else:
            log.info('Bypass /tmp/bypass')

    def __call__(self, *args, **kwargs):
        return self.do_stuff()
