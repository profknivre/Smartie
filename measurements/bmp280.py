import logging
import paho.mqtt.subscribe as subscribe
import json

from .base_measurement import BaseMeasurement

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

last_read_time = 0
last_read = 0, 0


class Bmp280(BaseMeasurement):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def read(self):
        humidity, temperature = 0, 0
        msg = subscribe.simple("tele/tasmota_0DCAF3/SENSOR", hostname="mqtt.lan")
        payload = json.loads(str(msg.payload, 'utf-8'))
        # {'Time': '2023-05-22T11:43:55',
        #  'BME280': {'Temperature': 22.6, 'Humidity': 48.8, 'DewPoint': 11.3, 'Pressure': 999.8}, 'PressureUnit': 'hPa',
        #  'TempUnit': 'C'}

        humidity = payload['BME280'].get('Humidity')
        temperature = payload['BME280'].get('Temperature')

        return humidity, temperature