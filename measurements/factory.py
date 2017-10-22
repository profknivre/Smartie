def get_measurements():
    from .base_measurement import BaseMeasurement

    _measurements = BaseMeasurement.__subclasses__()
    # _measurements = filter(lambda x: hasattr(x, 'REMOTE_CMD'), _measurements)

    return _measurements
