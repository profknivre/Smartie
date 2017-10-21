import logging
import shelve
from functools import lru_cache
from time import time

import requests

import config
from measurements.base_measurement import BaseMeasurement
from util import timeout

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class OnlineWeather(BaseMeasurement):
    instance = None
    def __init__(self, **kwargs):
        if 'timing_caption' not in kwargs:
            kwargs['timing_caption'] = 'malina0.measurments_time.apixu'
        super().__init__(**kwargs)

    def read(self):
        apixu = getdata()

        if 'current' not in apixu:
            log.error('"current" node not found')
            return -1, -1
        else:
            if 'temp_c' not in apixu['current'] or 'humidity' not in apixu['current']:
                log.error('"temp_c" node not found')
                return -1, -1

        temperature = apixu['current']['temp_c']
        humidity = apixu['current']['humidity']

        # return temperature, humidity
        return humidity, temperature

@lru_cache()  # speedup tests
def getdata():
    def _getdata_raw():
        # response = requests.get('http://api.apixu.com/v1/current.json?key=%s&q=Wroclaw'%('keystring'))
        # in my network 5.8.0.0/16 is not routed outside
        # this is a caching proxy running very similar code but it has api key embedded
        # log.info('Doing apixu request...')
        response = requests.get(config.apixu_link)
        # log.info('apixu req done')
        return response.json()

    # <editor-fold desc="example output">
    example_output = {
        'location': {
            'name': 'Wroclaw',
            'region': '',
            'country': 'Poland',
            'lat': 51.1,
            'lon': 17.03,
            'tz_id': 'Europe/Warsaw',
            'localtime_epoch': 1497957239,
            'localtime': '2017-06-20 13:13'
        },
        'current': {
            'last_updated_epoch': 1497956418,
            'last_updated': '2017-06-20 13:00',
            'temp_c': 31.0,
            'is_day': 1,
            'condition': {
                'text': 'Sunny',
                'icon': '//cdn.apixu.com/weather/64x64/day/113.png',
                'code': 1000
            },
            'wind_kph': 20.2,
            'wind_degree': 270,
            'wind_dir': 'W',
            'pressure_mb': 1014.0,
            'pressure_in': 30.4,
            'precip_mm': 0.0,
            'humidity': 33,
            'cloud': 0,
            'feelslike_c': 30.4,
            'vis_km': 10.0,
            'vis_miles': 6.0
        }
    }
    # </editor-fold>

    with shelve.open('/tmp/apixu_last_weather') as db:
        olddata = db.get('olddata', dict())
        need_update = False
        if 'current' in olddata:
            last_ts = olddata['current']['last_updated_epoch']

            if time() - last_ts >= 7 * 60:
                need_update = True
        else:
            need_update = True

        if need_update:
            try:
                with timeout(5):
                    olddata = _getdata_raw()
                    db['olddata'] = olddata
            except Exception as e:
                log.debug(e)

        return olddata
