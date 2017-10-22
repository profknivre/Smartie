from .coretemp import CoreTemp
from .dht import Dht
from .ds18 import Ds18
from .online_weather import OnlineWeather


def __dupa():
    a = [CoreTemp, Dht, Ds18, OnlineWeather]
    return a

def get_measurements():
    from .base_measurement import BaseMeasurement

    _measurements = BaseMeasurement.__subclasses__()
    # _measurements = filter(lambda x: hasattr(x, 'REMOTE_CMD'), _measurements)

    return _measurements
