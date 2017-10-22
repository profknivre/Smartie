import logging
from abc import ABC, abstractmethod
from contextlib import suppress
from logging.handlers import RotatingFileHandler
from time import time

import rpyc

import config
from util import ResourceMonitor

bf = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler('/tmp/smartie.log', maxBytes=10 * 1024 * 1024, backupCount=10)
handler.setFormatter(bf)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(config.loglevel)

log = logging.getLogger(__name__)

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


class ReadCoreTemp(BaseCommand):
    NAME = 'read_coretemp'

    def exec(self, **kwargs):
        from measurements.coretemp import CoreTemp
        return CoreTemp().read()


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
            lastq = store.get(lqs, 0)

            if time() - lastq > config.rpyc_cmd_retry_interval:
                retval = cmds.get(name).exec(**kwargs)
                store[lqs] = time()
                store[lqd] = retval
            else:
                retval = store[lqd]

            return retval


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer as RpycServer

    null_logger = logging.getLogger('nullloger')
    null_logger.setLevel(logging.ERROR)
    null_logger.handlers.clear()
    null_logger.addHandler(logging.NullHandler())

    registrar = rpyc.utils.registry.TCPRegistryClient('5.8.0.8', logger=null_logger)
    t = RpycServer(SmartieSlave, port=18861, auto_register=True, registrar=registrar, logger=null_logger)
    rm = ResourceMonitor()

    server = t

    with suppress(KeyboardInterrupt):
        rm.start()
        t.start()
