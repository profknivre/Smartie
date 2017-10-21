from contextlib import suppress

import rpyc

from util import timeout


class SmartieSlave(rpyc.Service):
    ALIASES = ['SmartieSlave']

    def on_connect(self):
        # code that runs when a connection is created
        # (to init the serivce, if needed)
        pass

    def on_disconnect(self):
        # code that runs when the connection has already closed
        # (to finalize the service, if needed)
        pass

    def exposed_get_ds18_temp(self, sensor_id):
        from measurements.ds18 import Ds18
        ds = Ds18(sensor_id='28-0115916115ff')

        retval = None
        with suppress(Exception):
            with timeout(seconds=5):
                retval = ds.read()

        return retval

    def exposed_get_dht_data(self):
        from measurements.dht import Dht
        dht = Dht(dht_read_params='Adafruit_DHT.DHT22, 19')
        retval = None
        with suppress(Exception):
            with timeout(seconds=5):
                retval = dht.read()

        return retval


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer

    t = ThreadedServer(SmartieSlave, port=18861, auto_register=True)
    t.start()
