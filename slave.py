import logging
import threading
from abc import ABC, abstractmethod
from contextlib import suppress
from logging.handlers import RotatingFileHandler
from time import time

import rpyc

import config

bf = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler('/tmp/smartie.log', maxBytes=10 * 1024 * 1024, backupCount=10)
handler.setFormatter(bf)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(config.loglevel)

log = logging.getLogger(__name__)


from time import sleep

# in my network 5.8.0.0/16 is not routed outside!!!
stats = config.stats_client

monitoring = True
server = None
store = dict()


class BaseCommand(ABC):
    def __init__(self, **kwargs):
        self.service = kwargs.get('service')
        super().__init__()

    @abstractmethod
    def exec(self, **kwargs):
        pass

    @staticmethod
    def build(**kwargs):
        ret = {}
        for cls in BaseCommand.__subclasses__():
            ret[cls.NAME] = cls(**kwargs)
        return ret


class ReadDs18(BaseCommand):
    NAME = 'read_ds18'

    def exec(self, **kwargs):
        from measurements.ds18 import Ds18
        ds = Ds18(**kwargs)  # 28-0115916115ff
        retval = ds.read()
        return retval


class ReadDHT(BaseCommand):
    NAME = 'read_dht'

    def exec(self, **kwargs):
        from measurements.dht import Dht
        dht = Dht(**kwargs)
        retval = dht.read()
        return retval


class Disconnect(BaseCommand):
    NAME = 'disconnect'

    def exec(self, **kwargs):
        self.service._conn.close()


class KillServer(BaseCommand):
    NAME = 'kill'

    def exec(self, **kwargs):
        if server is not None:
            server.close()

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

    def exposed_tst(self):
        Disconnect(service=self).exec()

    def exposed_cmd(self, name, **kwargs):
        cmds = BaseCommand.build(service=self)

        if name in cmds:
            lqs = 'last_{:s}_query'.format(name)
            lqd = 'last_{:s}_retval'.format(name)
            lastq = store.get(lqs, time())

            if time() - lastq > config.rpyc_cmd_retry_interval:
                retval = cmds.get(name).exec(**kwargs)
                store[lqs] = time()
                store[lqd] = retval
            else:
                retval = store[lqd]

            return retval


def worker():
    import psutil
    from platform import node

    hostname = node().replace('.lan', '')

    while True:
        pvm = psutil.virtual_memory()
        fields = ('used')  # , 'free')
        nfo = dict(filter(lambda x: x[0] in fields, zip(pvm._asdict(), pvm)))

        for k in nfo.keys():
            caption = '{}.memory.{}'.format(hostname, k)
            if monitoring:
                stats.gauge(caption, nfo.get(k))
                # print(caption, nfo.get(k))
        sleep(60)

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer as RpycServer

    registrar = rpyc.utils.registry.TCPRegistryClient('5.8.0.8')
    t = RpycServer(SmartieSlave, port=18861, auto_register=True, registrar=registrar)
    t2 = threading.Thread(target=worker, name='ResourceMonitor', daemon=True)

    server = t

    with suppress(KeyboardInterrupt):
        t2.start()
        t.start()
