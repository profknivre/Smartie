import logging

from measurements.base_measurement import BaseMeasurement

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Ds18(BaseMeasurement):
    def __init__(self, **kwargs):
        self.sensor_id = kwargs.get('sensor_id', '28-0115915119ff')
        self.sensor_path = '/sys/bus/w1/devices/{:s}/w1_slave'.format(self.sensor_id)

        if 'timing_caption' not in kwargs:
            kwargs['timing_caption'] = 'malina0.measurments_time.ds18read'

        super().__init__(**kwargs)

    def read(self):
        try:
            with open(self.sensor_path, 'r') as f:
                f.readline()
                b = f.readline()
                z = float(b.strip().split('=')[1]) / 1000.0
                return z
        except Exception as e:
            log.error(e)
            return 0
