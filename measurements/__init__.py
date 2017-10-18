import logging
import shelve
from collections import deque
from json import dump, load

from measurements.coretemp import CoreTemp
from measurements.dht import Dht
from measurements.ds18 import Ds18
from measurements.online_weather import OnlineWeather
from util import linreg, TimerMock, UberAdapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

try:
    import Adafruit_DHT
    import statsd
except ModuleNotFoundError as e:
    log.error(e)
    pass

# ---decorator hack
try:
    # in my network 5.8.0.0/16 is not routed outside!!!
    stats = statsd.StatsClient('5.8.1.1', 8125)
except NameError:
    stats = TimerMock


# ---/hack


class MeasurementsInternals2():
    class Sloper:  # UGLY
        def __init__(self, current_val_rdr):
            self.reader = current_val_rdr
            self.gauge_caption = 'mieszkanie.lazienka.humidity_slope'
            self.timing_caption = 'malina0.measurments_time.dhtread'

        def read(self):
            current_val = self.reader.read()

            with shelve.open('/tmp/shelve') as db:
                dq = db.get('hum_hist', deque(maxlen=10))

                dq.append(current_val)
                db['hum_hist'] = dq
                log.debug('adding {} into history'.format(current_val))

                self.slope = linreg(range(len(dq)), dq)[0]

            return self.slope

    def __init__(self):
        dht = Dht()
        self.bathroom_temperature = UberAdapter(dht, 1, gauge_caption='mieszkanie.lazienka.temp')
        self.bathroom_humidity = UberAdapter(dht, 0, gauge_caption='mieszkanie.lazienka.humidity')
        self.bathroom_humidity_slope = self.Sloper(self.bathroom_humidity)  # !!! TODO fixme!!!

        ot = OnlineWeather()
        self.online_temperature = UberAdapter(ot, 1, gauge_caption='mieszkanie.temp_zew')
        self.online_humidity = UberAdapter(ot, 0, gauge_caption='mieszkanie.humi_zew')

        self.saloon_temperature = Ds18(sensor_id='28-0115915119ff', gauge_caption='mieszkanie.temp1')
        self.core_temperature = CoreTemp(gauge_caption='malina0.core_temp')


class Measurements():
    def __init__(self):
        m = MeasurementsInternals2()

        timed = set()
        gaged = set()

        for k, v in vars(m).items():
            if hasattr(v, 'timing_caption') and v.timing_caption not in timed:
                with stats.timer(v.timing_caption):
                    # log.debug('timing: {}'.format(v.timing_caption))
                    value = v.read()
                    timed.add(v.timing_caption)
            else:
                # log.debug('not timing: {}'.format(k))
                value = v.read()

            if hasattr(v, 'gauge_caption') and v.gauge_caption not in gaged:
                stats.gauge(v.gauge_caption, value)
                gaged.add(v.gauge_caption)
                # log.debug('stat {}:{}'.format(v.gauge_caption, value))
            setattr(self, k, value)

        self.dump()

    def __str__(self) -> str:
        return "Saloon temp: {:2.1f} bathroom temp: {:2.1f} bathroom humidity: {:2.1f}%" \
            .format(self.saloon_temperature, self.bathroom_temperature, self.bathroom_humidity)

    # def __del__(self):
    #     log.debug('Deleting {}'.format(repr(self)))

    def load(self, fname):
        with open(fname, 'r') as f:
            dct = load(f)
            vars(self).update(dct)

    def save(self, fname):
        dct = vars(self)
        with open(fname, 'w') as f:
            dump(dct, f)

    def dump(self):
        for k, v in vars(self).items():
            if isinstance(v, float):
                v = round(v, 2)
            log.debug('{}:{}'.format(k, v))
