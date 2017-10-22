import logging

import statsd

from util import TimerMock

loglevel = logging.DEBUG

# in my network 5.8.0.0/16 is not routed outside!!!
try:
    import Adafruit_DHT

    stats_client = statsd.StatsClient('5.8.1.1', 8125)
except ModuleNotFoundError:  # not on raspi, skip statsd
    stats_client = TimerMock

# see pi_zero_pinout.txt
fan_gpio_settings = {'pinnumber': 13}

# response = requests.get('http://api.apixu.com/v1/current.json?key=%s&q=Wroclaw'%('keystring'))
# in my network 5.8.0.0/16 is not routed outside
# this is a caching proxy running very similar code but it has api key embedded
apixu_link = 'http://5.8.0.1/cgi-bin/zonk.py'

# minimise fan running time between 23:00 and 05:00
weekend_quiet_hours = list(range(0, 6)) + list(range(23, 24))

fan_runtime_min_quiet = 5 * 60
fan_runtime_max_quiet = 15 * 60

fan_runtime_min = 15 * 60
fan_runtime_max = 60 * 60

dht_read_params = 'Adafruit_DHT.DHT22, 19'

rpyc_cmd_retry_interval = 30
