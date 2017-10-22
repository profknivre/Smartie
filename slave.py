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
        vars(self).update(kwargs)
        super().__init__()

    @abstractmethod
    def exec(self, **kwargs):
        pass

    @staticmethod
    def build(**kwargs):
        ret = {}
        from measurements.factory import get_measurements
        _measurements = get_measurements()
        _measurements = filter(lambda x: hasattr(x, 'REMOTE_CMD'), _measurements)

        for cls in _measurements:
            ret[cls.REMOTE_CMD] = MeasurementCommand(cls=cls, **kwargs)

        _commands = BaseCommand.__subclasses__()
        _commands = filter(lambda x: hasattr(x, 'NAME'), _commands)
        for cls in _commands:
            ret[cls.NAME] = cls(**kwargs)

        return ret


class MeasurementCommand(BaseCommand):
    def exec(self, **kwargs):
        obj = self.cls(**kwargs)
        return obj.read()

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
