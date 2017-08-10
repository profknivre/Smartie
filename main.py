#!/usr/bin/python3

import logging
import shelve
from datetime import timedelta
from time import ctime

from fan import TimedFan
from fanctrl import FanController
from gpio import SysfsGPIO
from measurements import TimedMeasurements
from util import TimerMock

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG,
                    filename='/tmp/smartie.log')

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


try:
    import statsd
except ModuleNotFoundError:
    pass

# TODO make this proper
# ---decorator hack
try:
    # in my network 5.8.0.0/16 is not routed outside!!!
    stats = statsd.StatsClient('5.8.1.1', 8125)
except NameError:
    stats = TimerMock


# ---/hack

class ActualFan(TimedFan):
    def __init__(self):
        gp = SysfsGPIO(pinnumber=13)
        if gp.getDDR() == gp.DDR_INPUT:
            gp.setDDR(gp.DDR_OUTPUT)

        self.database_ = shelve.open('/tmp/fan_data')
        super().__init__(gp, self.database_)

    def on(self, who):
        log.debug('Enabled by {} @ {}\n'.format(
                who, ctime()))
        return super().on(who)

    def off(self, who):
        log.debug('Disabled by {} @ {}\n'.format(who, ctime()))
        log.debug('{} fan was ruining for: {}({:.0f}s)\n'.format(
                ctime(), timedelta(seconds=self.on_time()), self.on_time()))
        return TimedFan.off(self, who)

    def __del__(self):
        self.database_.close()


def main():
    log.info('sztartin...')
    with stats.timer('malina0.measurments_time.total'):
        m = TimedMeasurements()

        stats.gauge('mieszkanie.temp1', m.ds18temp)
        stats.gauge('malina0.core_temp', m.coretemp)
        stats.gauge('mieszkanie.lazienka.temp', m.temperature)
        stats.gauge('mieszkanie.lazienka.humidity', m.humidity)
        stats.gauge('mieszkanie.lazienka.humidity_slope', m.slope)
        stats.gauge('mieszkanie.temp_zew', m.apixtemp)
        stats.gauge('mieszkanie.humi_zew', m.apixhum)

        fan = ActualFan()
        fc = FanController(fan, m)
        fc.do_stuff()

        stats.gauge('mieszkanie.lazienka.wentylator', int(fan.is_on()))

        # TODO pretty print this shite
        log.info(str(m))


if __name__ == '__main__':
    main()
