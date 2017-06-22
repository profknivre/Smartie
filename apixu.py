import shelve
import signal
from contextlib import suppress
from time import time
import json
import requests


class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


def _getdata_raw():
    # response = requests.get('http://api.apixu.com/v1/current.json?key=%s&q=Wroclaw'%('keystring'))
    # in my network 5.8.0.0/16 is not routed outside
    # this is a caching proxy running very similar code but it has api key embedded
    response = requests.get('http://5.8.0.1/cgi-bin/zonk.py')
    return response.json()


def _getdata_raw_():
    return {
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


def getdata():
    with shelve.open('/tmp/apixu_last_weather') as db:
        if 'olddata' in db:
            olddata = db['olddata']
        else:
            olddata = dict()

        need_update = False
        if 'current' in olddata:
            last_ts = olddata['current']['last_updated_epoch']

            if time() - last_ts >= 15 * 60:
                need_update = True
        else:
            need_update = True

        if not need_update: return olddata
        with suppress((Exception)):
            with timeout(5):
                olddata = _getdata_raw()
                db['olddata'] = olddata

        return olddata

