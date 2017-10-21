import logging
from json import dump, load

from util import TimerMock

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

try:
    import Adafruit_DHT
    import statsd
except ModuleNotFoundError as e:
    log.error(e)
    pass

# ---decorator hack
try:
    # in my network 5.8.0.0/16 is not routed outside!!!
    stats = statsd.StatsClient('5.8.1.1', 8125)
except NameError:
    stats = TimerMock


# ---/hack


class Measurements():
    def __init__(self):
        import measurements.mesurement_internals

        m = measurements.mesurement_internals.MeasurementsInternals2()

        timed = set()
        gaged = set()

        for k, v in vars(m).items():
            if hasattr(v, 'timing_caption') and v.timing_caption not in timed:
                with stats.timer(v.timing_caption):
                    # log.debug('timing: {}'.format(v.timing_caption))
                    value = v.read()
                    timed.add(v.timing_caption)
            else:
                # log.debug('not timing: {}'.format(k))
                value = v.read()

            if hasattr(v, 'gauge_caption') and v.gauge_caption not in gaged:
                stats.gauge(v.gauge_caption, value)
                gaged.add(v.gauge_caption)
                # log.debug('stat {}:{}'.format(v.gauge_caption, value))
            setattr(self, k, value)

        self.dump()

    def __str__(self) -> str:
        return "Saloon temp: {:2.1f} bathroom temp: {:2.1f} bathroom humidity: {:2.1f}%" \
            .format(self.saloon_temperature, self.bathroom_temperature, self.bathroom_humidity)

    # def __del__(self):
    #     log.debug('Deleting {}'.format(repr(self)))

    def load(self, fname):
        with open(fname, 'r') as f:
            dct = load(f)
            vars(self).update(dct)

    def save(self, fname):
        dct = vars(self)
        with open(fname, 'w') as f:
            dump(dct, f)

    def dump(self):
        for k, v in vars(self).items():
            if isinstance(v, float):
                v = round(v, 2)
            log.debug('{}:{}'.format(k, v))
