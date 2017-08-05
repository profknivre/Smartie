#!/usr/bin/python

import os
import shelve
import subprocess
from collections import deque
from time import ctime

from fan import Fan
from gpio import SysfsGPIO
from util import linreg, TimerMock

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


# ---/hack

# TODO: add some testing!!


def get_slope(current_val, update=True):
    with shelve.open('/tmp/shelve') as db:
        dq = db.get('hum_hist', deque(maxlen=10))
        dq3 = db.get('hum_hist3', deque(maxlen=3))

        if update:
            dq.append(current_val)
            db['hum_hist'] = dq
            dq3.append(current_val)
            db['hum_hist3'] = dq3

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

    if 'current' not in apixu:
        print('apixu broken')
        return (-1, -1)
    else:
        if 'temp_c' not in apixu or 'humidity' not in apixu:
            print('apixu broken')
            return (-1, -1)

    temperature = apixu['current']['temp_c']
    humidity = apixu['current']['humidity']

    return temperature, humidity


def fan_control(humidity):
    def log_fan_time(fan):
        with open('/tmp/fanlog', 'at') as f:
            ontime = fan.on_time_last()
            str = '{}:Fan on time: {}\n'.format(ctime(), ontime)
            f.write(str)


    slope = get_slope(humidity)
    stats.gauge('mieszkanie.lazienka.humidity_slope', slope)

    if not os.path.exists('/tmp/bypass'):
        gp = SysfsGPIO(pinnumber=13)
        if gp.getDDR() == gp.DDR_INPUT:
            gp.setDDR(gp.DDR_OUTPUT)

        with shelve.open('/tmp/fan_data') as db:
            fan = Fan(gp, db)

            if humidity >= 80 and slope >= 1:
                fan.on()

            if humidity < 80 and slope > -0.25:  # and fan.on_time() > (15*60):
                fan.off()
                log_fan_time(fan)

            if humidity < 50 or fan.on_time() > 3600:
                fan.off()
                log_fan_time(fan)

            val = fan.is_on()
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

        fan_control(humidity)

        # TODO pretty print this shite
        print("temp1: {:2.2f} temp lazienka: {:2.2f} humi lazienka: {:2.2f}".format(ds18temp, temperature, humidity))


if __name__ == '__main__':
    main()
