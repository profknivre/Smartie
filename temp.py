#!/usr/bin/python

import os
import shelve
import subprocess
from collections import deque

import Adafruit_DHT
import statsd
from apixu import getdata

c = statsd.StatsClient('5.8.1.1', 8125)


def get_slope(current_val, update=True):

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


def readds18():
    with open('/sys/bus/w1/devices/28-0115915119ff/w1_slave', 'r') as f:
        f.readline()
        b = f.readline()
        z = float(b.strip().split('=')[1]) / 1000.0
        return z


def readcroetemp():
    return float(
        subprocess.check_output(['/opt/vc/bin/vcgencmd', 'measure_temp']).decode('utf8').strip()[5:].replace("'C", ''))


def fancontrol(humidity, humi_slope):
    if not os.path.exists('/tmp/bypass'):
        if not os.path.exists('/sys/class/gpio/gpio13/value'):
            with open('/sys/class/gpio/export', 'w') as file:
                file.write('13\n')

            with open('/sys/class/gpio/gpio13/direction', 'w') as file:
                file.write('out\n')

            with open('/sys/class/gpio/gpio13/value', 'w') as file:
                file.write('0\n')

        if humidity >= 80:
            with open('/sys/class/gpio/gpio13/value', 'w') as file:
                file.write('1\n')

        # if humidity <=65:
        if humidity < 75 and abs(humi_slope) < 0.25:
            with open('/sys/class/gpio/gpio13/value', 'w') as file:
                file.write('0\n')

        if not os.path.exists('/sys/class/gpio/gpio13/value'):
            raise Exception('no gpio')

    with open('/sys/class/gpio/gpio13/value') as file:
        val = int(file.read().strip())
        c.gauge('mieszkanie.lazienka.wentylator', val)


with c.timer('malina0.measurments_time.total'):
    with c.timer('malina0.measurments_time.ds18read'):
        ds18temp = readds18()
        c.gauge('mieszkanie.temp1', ds18temp)

    with c.timer('malina0.measurments_time.coretemp'):
        tmp = readcroetemp()
        c.gauge('malina0.core_temp', tmp)

    with c.timer('malina0.measurments_time.dhtread'):
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 19)

    c.gauge('mieszkanie.lazienka.temp', temperature)
    c.gauge('mieszkanie.lazienka.humidity', humidity)

    humi_slope = get_slope(humidity)

    c.gauge('mieszkanie.lazienka.humidity_slope', humi_slope)

    # TODO pretty print this shite
    print("temp1: {:2.2f} temp lazienka: {:2.2f} humi lazienka: {:2.2f}".format(ds18temp, temperature, humidity))

    with c.timer('malina0.measurments_time.apixu'):
        apixu = getdata()
    temp = apixu['current']['temp_c']
    ahum = apixu['current']['humidity']

    c.gauge('mieszkanie.temp_zew', temp)
    c.gauge('mieszkanie.humi_zew', ahum)

    fancontrol(humidity, humi_slope)
