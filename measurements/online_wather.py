import logging

from measurements.base_measurement import BaseMeasurement

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from apixu import getdata


class OnlineWeather(BaseMeasurement):
    def __init__(self, **kwargs):
        if 'timing_caption' not in kwargs:
            kwargs['timing_caption'] = 'malina0.measurments_time.apixu'
        super().__init__(**kwargs)

    def read(self):
        apixu = getdata()

        if 'current' not in apixu:
            log.error('apixu broken')
            return -1, -1
        else:
            if 'temp_c' not in apixu['current'] or 'humidity' not in apixu['current']:
                log.error('apixu broken2')
                return -1, -1

        temperature = apixu['current']['temp_c']
        humidity = apixu['current']['humidity']

        # return temperature, humidity
        return humidity, temperature


class OnlineTemperature(OnlineWeather):
    def read(self):
        return super().read()[1]


class OnlineHumidity(OnlineWeather):
    def read(self):
        return super().read()[0]
