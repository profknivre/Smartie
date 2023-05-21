import logging
import shelve
from collections import deque

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from .dht import Dht
from .online_weather import OnlineWeather
from .ds18 import Ds18
from .coretemp import CoreTemp

import config

from util import linreg, UberAdapter, RemoteAdapter, timeout



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
                log.debug('adding {:.02f} into history'.format(current_val))

                self.slope = linreg(range(len(dq)), dq)[0]

            return self.slope

    def __init__(self):
        dht = Dht(dht_read_params=config.dht_read_params)
        self.bathroom_temperature = UberAdapter(dht, 1, gauge_caption='mieszkanie.lazienka.temp')
        self.bathroom_humidity = UberAdapter(dht, 0, gauge_caption='mieszkanie.lazienka.humidity')
        self.bathroom_humidity_slope = self.Sloper(self.bathroom_humidity)  # !!! TODO fixme!!!

#        ot = OnlineWeather()
#        self.online_temperature = UberAdapter(ot, 1, gauge_caption='mieszkanie.temp_zew')
#        self.online_humidity = UberAdapter(ot, 0, gauge_caption='mieszkanie.humi_zew')

        self.saloon_temperature = Ds18(sensor_id='28-0115915119ff', gauge_caption='mieszkanie.temp1')
        self.core_temperature = CoreTemp(gauge_caption='malina0.core_temp')

#        try:
#            with timeout(5):
#                # import rpyc
#                # registrar = rpyc.utils.registry.TCPRegistryClient('5.8.0.8')
#                # ret = rpyc.utils.factory.discover('SmartieSlave', registrar=registrar)
#                # conn = rpyc.connect(*ret[0])
#
#                from disco import DiscoProxy2
#                dp2=DiscoProxy2()
#
#                conn = dp2.SmartieSlave
#
#                self.radiator_temperature = RemoteAdapter(Ds18, gauge_caption='mieszkanie.kaloryfer.temp',
#                                                          sensor_id='28-0115916115ff', conn=conn)
#    
#                remote_dht = RemoteAdapter(Dht, dht_read_params='Adafruit_DHT.DHT22, 4', conn=conn,
#                                           timing_caption='malina2.measurments_time.dht22read')
#    
#                self.bedroom_temperature = UberAdapter(remote_dht, 1, gauge_caption='mieszkanie.test22.temp')
#                self.bedroom_humidity = UberAdapter(remote_dht, 0, gauge_caption='mieszkanie.test22.humidity')
#    
#                self.malina2_core_temperature = RemoteAdapter(CoreTemp, gauge_caption='malina2.core_temp',
#                                                              timing_caption='malina2.measurments_time.coretemp',
#                                                              conn=conn)
#
#        except Exception as e:
#            log.exception(e)
