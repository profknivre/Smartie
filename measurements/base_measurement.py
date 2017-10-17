import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class BaseMeasurement:
    def __init__(self, **kwargs):
        self.timing_caption = kwargs.get('timing_caption', 'malina0.measurments_time.{:s}'.format(
            str(self.__class__.__name__.lower())))

        self.gauge_caption = kwargs.get('gauge_caption', str(self.__class__.__name__.lower()))
