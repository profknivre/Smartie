#!/usr/bin/python3

import logging
import shelve
from datetime import timedelta
from logging.handlers import RotatingFileHandler
from time import time

import config
from fan import TimedFan
from fanctrl import FanController
from gpio import SysfsGPIO
from measurements import Measurements
from measurements.historian import engrave, extract_run
from util import TimerMock, ResourceMonitor, XZRotator, XZNamer, FileMutex

bf = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler('/tmp/smartie.log', maxBytes=5 * 1024 * 1024, backupCount=100)
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
        log.debug('Enabled by {}'.format(
            who))
        return super().on(who)

    def off(self, who=None):
        log.debug('Disabled by {}'.format(who))
        log.debug('fan was ruining for: {}({:.0f}s)'.format(
            timedelta(seconds=self.on_time()), self.on_time()))

        ot = 10 + self.on_time() // 60
        extract_run(minutes=ot)

        return TimedFan.off(self, who)

    def __del__(self):
        self.database_.close()


def main():
    log.info('sztartin...')
    rm = ResourceMonitor()
    rm.start()

    with stats.timer('malina0.measurments_time.total'):
        with stats.timer('malina0.measurments_time.measurements'):
            m = Measurements()

        fan = ActualFan()
        fc = FanController(fan, m)
        fc.do_stuff()
        stats.gauge('mieszkanie.lazienka.wentylator', int(fan.is_on()))

        m.fan_state = int(fan.is_on())
        # m.timestamp = str(datetime.now().strftime('%Y%m%d%H%M'))  # redundant
        m.unix_timestamp = time()
        with stats.timer('malina0.measurments_time.engrave'):
            engrave(m, 60 * 24 * 7)  # keep one week of historical data

if __name__ == '__main__':
    with FileMutex():   # log rotation/compression is _really_ _slow_ on RPi Zero
        try:
            main()
        except Exception as e:
            log.exception(e)
