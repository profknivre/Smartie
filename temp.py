#!/usr/bin/python

import os
import shelve
import subprocess
from collections import deque

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
    class TimerMock:
        @staticmethod
        def timer(args):
            def a(arg):
                pass
            return a
    stats = TimerMock
# ---hack

# TODO: add some testing!!


def linreg(x, y):
    """
    return a,b in solution to y = ax + b such that root mean square distance between trend line
    and original points is minimized
    """
    n = len(x)
    sx = sy = sxx = syy = sxy = 0.0
    for x_, y_ in zip(x, y):
        sx = sx + x_
        sy = sy + y_
        sxx = sxx + x_ * x_
        syy = syy + y_ * y_
        sxy = sxy + x_ * y_
    det = sxx * n - sx * sx
    try:
        return (sxy * n - sy * sx) / det, (sxx * sy - sx * sxy) / det
    except ZeroDivisionError:
        return 0


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


def fancontrol(humidity, slope):
    pin =13
    prefix = '/sys/class/gpio/'
    gpio = 'gpio{}'.format(pin)
    value_path = '{}{}/value'.format(prefix,gpio)
    direction_path = '{}{}/direction'.format(prefix,gpio)

    if not os.path.exists('/tmp/bypass'):
        if not os.path.exists(value_path):
            with open('/sys/class/gpio/export', 'w') as file:
                file.write('13\n')

            with open(direction_path, 'w') as file:
                file.write('out\n')

            with open(value_path, 'w') as file:
                file.write('0\n')

        if humidity >= 80:
            with open(value_path, 'w') as file:
                file.write('1\n')

        # if humidity <=65:
        if humidity < 75 and abs(slope) < 0.25:
            with open(value_path, 'w') as file:
                file.write('0\n')

        if not os.path.exists(value_path):
            raise Exception('no gpio')

    with open(value_path) as file:
        val = int(file.read().strip())
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

        slope = get_slope(humidity)

        stats.gauge('mieszkanie.lazienka.humidity_slope', slope)

        # TODO pretty print this shite
        print("temp1: {:2.2f} temp lazienka: {:2.2f} humi lazienka: {:2.2f}".format(ds18temp, temperature, humidity))

        apixtemp, apixhum = readapixu()

        stats.gauge('mieszkanie.temp_zew', apixtemp)
        stats.gauge('mieszkanie.humi_zew', apixhum)

        fancontrol(humidity, slope)


if __name__ == '__main__':
    main()
