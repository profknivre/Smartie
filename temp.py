#!/usr/bin/python3

import shelve
from datetime import timedelta
from time import ctime

from fan import Fan
from fanctrl import FanController
from gpio import SysfsGPIO
from measurements import TimedMeasurements
from util import TimerMock

try:
    import Adafruit_DHT
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

class ActualFan(Fan):
    def __init__(self):
        gp = SysfsGPIO(pinnumber=13)
        if gp.getDDR() == gp.DDR_INPUT:
            gp.setDDR(gp.DDR_OUTPUT)

        self.database_ = shelve.open('/tmp/fan_data')
        super().__init__(gp, self.database_)

    def off(self):
        with open('/tmp/fanlog.txt', 'at') as f:
            f.write('{} fann was ruuning for: {}\n'.format(ctime(), timedelta(seconds=self.on_time())))
        Fan.off(self)

    def __del__(self):
        self.database_.close()


def main():
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

        val = fan.is_on()
        if val is True:
            val = 1
        else:
            val = 0

        stats.gauge('mieszkanie.lazienka.wentylator', val)

        # TODO pretty print this shite
        print(str(m))


if __name__ == '__main__':
    main()
