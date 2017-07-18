#!/usr/bin/python

import os
import shelve
import subprocess
from collections import deque

from util import linreg, TimerMock

from gpio import SysfsGPIO

try:
    import Adafruit_DHT
    import statsd
except ModuleNotFoundError:
    pass

from apixu import getdata

# TODO make this proper
# ---decorator hack
try:
    # in my network 5.8.0.0/16 is not routed outside!!!
    stats = statsd.StatsClient('5.8.1.1', 8125)
except NameError:
    stats = TimerMock


# ---hack

# TODO: add some testing!!


def get_slope(current_val, update=True):
    with shelve.open('/tmp/shelve') as db:
        if 'hum_hist' not in db:
            dq = deque(maxlen=10)
            if current_val == 0:
                dq.append(-1)
        else:
            dq = db['hum_hist']

        if update:
            dq.append(current_val)
            db['hum_hist'] = dq

        a, b = linreg(range(len(dq)), dq)

        return a


@stats.timer('malina0.measurments_time.ds18read')
def readds18():
    with open('/sys/bus/w1/devices/28-0115915119ff/w1_slave', 'r') as f:
        f.readline()
        b = f.readline()
        z = float(b.strip().split('=')[1]) / 1000.0
        return z


@stats.timer('malina0.measurments_time.coretemp')
def readcroetemp():
    return float(
        subprocess.check_output(['/opt/vc/bin/vcgencmd', 'measure_temp']).decode('utf8').strip()[5:].replace("'C", ''))


@stats.timer('malina0.measurments_time.dhtread')
def readdht():
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 19)
    return humidity, temperature


@stats.timer('malina0.measurments_time.apixu')
def readapixu():
    apixu = getdata()
    temperature = apixu['current']['temp_c']
    humidity = apixu['current']['humidity']

    return temperature, humidity


def fancontrol(humidity):
    slope = get_slope(humidity)
    stats.gauge('mieszkanie.lazienka.humidity_slope', slope)

    if not os.path.exists('/tmp/bypass'):
        gp = SysfsGPIO(pinnumber=13)
        gp.setDDR(gp.DDR_OUTPUT)

        if humidity >= 80 and slope >= 1:
            gp.setOutput(1)

        if humidity < 80 and slope > -0.25:
            gp.setOutput(0)

        if humidity < 50:
            gp.setOutput(0)

        val = gp.getInput()
        stats.gauge('mieszkanie.lazienka.wentylator', val)


def main():
    with stats.timer('malina0.measurments_time.total'):
        ds18temp = readds18()
        stats.gauge('mieszkanie.temp1', ds18temp)

        coretemp = readcroetemp()
        stats.gauge('malina0.core_temp', coretemp)

        humidity, temperature = readdht()
        stats.gauge('mieszkanie.lazienka.temp', temperature)
        stats.gauge('mieszkanie.lazienka.humidity', humidity)

        apixtemp, apixhum = readapixu()
        stats.gauge('mieszkanie.temp_zew', apixtemp)
        stats.gauge('mieszkanie.humi_zew', apixhum)

        fancontrol(humidity)

        # TODO pretty print this shite
        print("temp1: {:2.2f} temp lazienka: {:2.2f} humi lazienka: {:2.2f}".format(ds18temp, temperature, humidity))


if __name__ == '__main__':
    main()
