import logging

from measurements.base_measurement import BaseMeasurement

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

last_read_time = 0
last_read = 0, 0


class Dht(BaseMeasurement):
    def __init__(self, **kwargs):
        if 'timing_caption' not in kwargs:
            kwargs['timing_caption'] = 'malina0.measurments_time.dhtread'
        self.dht_read_params = kwargs.get('dht_read_params', 'Adafruit_DHT.DHT22, 19')  # TODO: ugly as fuck
        super().__init__(**kwargs)

    def read(self):
        humidity, temperature = 0, 0
        try:
            import Adafruit_DHT
            humidity, temperature = Adafruit_DHT.read_retry(*eval(self.dht_read_params))  # TODO: ugly as fuck
        except Exception as e:
            log.error(e)

        return humidity, temperature
