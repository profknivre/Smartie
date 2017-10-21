import logging
import shelve
from collections import deque

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from .dht import Dht
from .online_weather import OnlineWeather
from .ds18 import Ds18
from .coretemp import CoreTemp
from util import linreg, UberAdapter


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
