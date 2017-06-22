#!/usr/bin/python

import os
import statsd
import subprocess
import Adafruit_DHT

from collections import deque
import pickle
from apixu import getdata

fname = '/tmp/histogram'

c = statsd.StatsClient('5.8.1.1', 8125)

def linreg(X, Y):
    """
    return a,b in solution to y = ax + b such that root mean square distance between trend line and original points is minimized
    """
    N = len(X)
    Sx = Sy = Sxx = Syy = Sxy = 0.0
    for x, y in zip(X, Y):
        Sx = Sx + x
        Sy = Sy + y
        Sxx = Sxx + x*x
        Syy = Syy + y*y
        Sxy = Sxy + x*y
    det = Sxx * N - Sx * Sx
    return (Sxy * N - Sy * Sx)/det, (Sxx * Sy - Sx * Sxy)/det


with c.timer('malina0.measurments_time'):
    z=0.0
    
    try:
        with open(fname,'rb') as f:
            humtab = pickle.loads(f.read())

    except:
        humtab = deque(maxlen=10)


    with c.timer('malina0.measurments_time.ds18read'):
        with open('/sys/bus/w1/devices/28-0115915119ff/w1_slave','r') as f:
            a = f.readline()
            b = f.readline()
            z=float(b.strip().split('=')[1])/1000.0
    
    c.gauge('mieszkanie.temp1', z)
    
    tmp=0.0
    with c.timer('malina0.measurments_time.coretemp'):
        tmp = float(subprocess.check_output(['/opt/vc/bin/vcgencmd','measure_temp']).decode('utf8').strip()[5:].replace("'C",''))
    
    c.gauge('malina0.core_temp', tmp)
    
    sensor = Adafruit_DHT.DHT22
    pin = 19
   
    humidity =0
    temperature =0

    with c.timer('malina0.measurments_time.dhtread'):
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    
    c.gauge('mieszkanie.lazienka.temp',temperature)
    c.gauge('mieszkanie.lazienka.humidity',humidity)

    humtab.append(humidity)

    humlst = list(humtab)
    a,b = linreg(range(len(humlst)),humlst)

    if 1 < 0:  c.gauge('mieszkanie.lazienka.humidity_slope',0.0)
    c.gauge('mieszkanie.lazienka.humidity_slope',a)

    print("slope {} {}".format(a,humlst))
    
    print("temp1: {:2.2f} temp lazienka: {:2.2f} humi lazienka: {:2.2f}".format(z,temperature,humidity))

    with c.timer('malina0.measurments_time.apixu'):
        apixu = getdata()
    temp = apixu['current']['temp_c']
    ahum = apixu['current']['humidity']

    c.gauge('mieszkanie.temp_zew', temp)
    c.gauge('mieszkanie.humi_zew', ahum)

    
    if not os.path.exists('/tmp/bypass'):
        if not os.path.exists('/sys/class/gpio/gpio13/value'):
            with open('/sys/class/gpio/export','w') as file:
                file.write('13\n')
    
            with open('/sys/class/gpio/gpio13/direction','w') as file:
                file.write('out\n')
    
            with open('/sys/class/gpio/gpio13/value','w') as file:
                file.write('0\n')
    
        if humidity >=80:
            with open('/sys/class/gpio/gpio13/value','w') as file:
                file.write('1\n')
       
        #if humidity <=65:
        if humidity < 75 and abs(a) < 0.25:
            with open('/sys/class/gpio/gpio13/value','w') as file:
                file.write('0\n')
    
    
        
        if not os.path.exists('/sys/class/gpio/gpio13/value'):
            raise Exception('no gpio')
    
    
        with open('/sys/class/gpio/gpio13/value') as file:
            val = int(file.read().strip())
            c.gauge('mieszkanie.lazienka.wentylator',val)

    with open(fname,'wb') as f:
        f.write(pickle.dumps(humtab))


