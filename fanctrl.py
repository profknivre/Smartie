import os

from conditions import *
from fan import TimedFan
from measurements import Measurements

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

modules = dir()

class FanController:
    def __init__(self, fan: TimedFan, measurements: Measurements):
        global modules
        self.fan = fan
        self.measurements = measurements

        conditions = list(filter(lambda x: 'Condition' in x, modules))
        # print(conditions)
        self.startconds = []
        self.stopconds = []

        for cond in conditions:
            cls = eval(cond)
            if issubclass(cls, FanStartCond):
                self.startconds.append(cls(self.fan, self.measurements))
            elif issubclass(cls, FanStopCond):
                self.stopconds.append(cls(self.fan, self.measurements))
            else:
                log.error('{:s} is neither FanStartCond nor FanStopCond'.format(cond))

    def do_stuff(self):
        if not os.path.exists('/tmp/bypass'):
            if any(self.startconds):
                log.info('Fan started')
            if any(self.stopconds):
                log.info('Fan stopped')
        else:
            log.info('Bypass /tmp/bypass')
