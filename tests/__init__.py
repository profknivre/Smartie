import logging

logging.getLogger().setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
bf = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(bf)

logging.getLogger().addHandler(ch)


fields = """bathroom_temperature
bathroom_humidity
bathroom_humidity_slope
online_temperature
online_humidity
saloon_temperature
core_temperature
radiator_temperature
bedroom_temperature
bedroom_humidity
malina2_core_temperature
""".split()


class MeasurementMock():
    def __init__(self):
        for f in fields:
            setattr(self,f,0)
