#!/usr/bin/python3

import logging
import shelve
from datetime import timedelta
from logging.handlers import RotatingFileHandler
from time import ctime

import config
from fan import TimedFan
from fanctrl import FanController
from gpio import SysfsGPIO
from measurements import Measurements
from util import TimerMock, ResourceMonitor, XZRotator, XZNamer

#logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG,
#                   filename='/tmp/smartie.log')

bf = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler('/tmp/smartie.log', maxBytes=10*1024*1024, backupCount=100)
handler.setFormatter(bf)
handler.rotator = XZRotator
handler.namer = XZNamer
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(config.loglevel)

log = logging.getLogger(__name__)
try:
    import statsd
except ModuleNotFoundError:
    pass

# TODO make this proper
# ---decorator hack
try:
    # in my network 5.8.0.0/16 is not routed outside!!!
    stats = config.stats_client
except NameError:
    stats = TimerMock


# ---/hack

class ActualFan(TimedFan):
    def __init__(self):
        gp = SysfsGPIO(**config.fan_gpio_settings)
        if gp.getDDR() == gp.DDR_INPUT:
            gp.setDDR(gp.DDR_OUTPUT)

        self.database_ = shelve.open('/tmp/fan_data')
        super().__init__(gp, self.database_)

    def on(self, who=None):
        log.debug('Enabled by {} @ {}'.format(
                who, ctime()))
        return super().on(who)

    def off(self, who=None):
        log.debug('Disabled by {} @ {}'.format(who, ctime()))
        log.debug('{} fan was ruining for: {}({:.0f}s)'.format(
                ctime(), timedelta(seconds=self.on_time()), self.on_time()))
        return TimedFan.off(self, who)

    def __del__(self):
        self.database_.close()


def main():
    log.info('sztartin...')
    rm = ResourceMonitor()
    rm.start()

    with stats.timer('malina0.measurments_time.total'):
        m = Measurements()

        fan = ActualFan()
        fc = FanController(fan, m)
        fc.do_stuff()

        stats.gauge('mieszkanie.lazienka.wentylator', int(fan.is_on()))

        # TODO pretty print this shite
        log.info(str(m))


if __name__ == '__main__':
    main()
