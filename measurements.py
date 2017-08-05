import shelve
import subprocess
from collections import deque
from json import dump, load

from util import linreg, TimerMock

try:
    import Adafruit_DHT
    import statsd
except ModuleNotFoundError:
    pass

from apixu import getdata

# ---decorator hack
try:
    # in my network 5.8.0.0/16 is not routed outside!!!
    stats = statsd.StatsClient('5.8.1.1', 8125)
except NameError:
    stats = TimerMock


# ---/hack


class MeasurmentsInternals:
    @staticmethod
    def read_ds18():
        try:
            with open('/sys/bus/w1/devices/28-0115915119ff/w1_slave', 'r') as f:
                f.readline()
                b = f.readline()
                z = float(b.strip().split('=')[1]) / 1000.0
                return z
        except:
            return 0

    @staticmethod
    def read_croetemp():
        try:
            return float(
                subprocess.check_output(['/opt/vc/bin/vcgencmd', 'measure_temp'])
                    .decode('utf8').strip()[5:].replace("'C", ''))
        except:
            return 0

    @staticmethod
    def read_dht():
        humidity, temperature = 0, 0
        try:
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 19)
        except:
            pass

        return humidity, temperature

    @staticmethod
    def read_apixu():
        apixu = getdata()

        if 'current' not in apixu:
            print('apixu broken')
            return -1, -1
        else:
            if 'temp_c' not in apixu['current'] or 'humidity' not in apixu['current']:
                print('apixu broken2')
                return -1, -1

        temperature = apixu['current']['temp_c']
        humidity = apixu['current']['humidity']

        return temperature, humidity

    @staticmethod
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


class Measurements(MeasurmentsInternals):
    def __init__(self):
        self.humidity, self.temperature = self.read_dht()
        self.slope = self.get_slope(self.humidity)
        self.ds18temp = self.read_ds18()
        self.apixtemp, self.apixhum = self.read_apixu()
        self.coretemp = self.read_croetemp()

    def __str__(self) -> str:
        return "Saloon temp: {:2.1f} bathroom temp: {:2.1f} bathroom humidity: {:2.1f}%" \
            .format(self.ds18temp, self.temperature, self.humidity)

    def load(self, fname):
        with open(fname, 'r') as f:
            dct = load(f)
            vars(self).update(dct)

    def save(self, fname):
        dct = vars(self)
        with open(fname, 'w') as f:
            dump(dct, f)


class TimedMeasurements(Measurements):
    @staticmethod
    def read_apixu():
        with stats.timer('malina0.measurments_time.apixu'):
            return super().read_apixu()

    @staticmethod
    def read_ds18():
        with stats.timer('malina0.measurments_time.ds18read'):
            return super().read_ds18()

    @staticmethod
    def read_dht():
        with stats.timer('malina0.measurments_time.dhtread'):
            return super().read_dht()

    @staticmethod
    def read_croetemp():
        with stats.timer('malina0.measurments_time.coretemp'):
            return super().read_croetemp()
