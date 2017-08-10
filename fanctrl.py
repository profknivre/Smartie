import logging

from conditions import *
from fan import TimedFan
from measurements import Measurements

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FanController:
    def __init__(self, fan: TimedFan, measurements: Measurements):
        self.fan = fan
        self.measurements = measurements

        self.startconds = [HighHumidityAndHighSlopeCondtion(self.fan, self.measurements),
                           ForceStartCondition(self.fan, self.measurements)]

        self.stopconds = [LowHumiditySmallSlopeCondition(self.fan, self.measurements),
                          LongRunningTimeCondition(self.fan, self.measurements),
                          ForceStopCondition(self.fan, self.measurements)]


    def do_stuff(self):
        if not os.path.exists('/tmp/bypass'):
            if any(self.startconds):
                log.info('Fan started')
            if any(self.stopconds):
                log.info('Fan stopped')
        else:
            log.info('Bypass /tmp/bypass')
