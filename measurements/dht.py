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
        super().__init__(**kwargs)

    def read(self):
        humidity, temperature = 0, 0
        try:
            import Adafruit_DHT
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 19)
        except Exception as e:
            log.error(e)

        return humidity, temperature
