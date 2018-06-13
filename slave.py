import logging
from abc import ABC, abstractmethod
from contextlib import suppress
from logging.handlers import RotatingFileHandler
from time import time
from xmlrpc.server import DocXMLRPCServer
import os

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


class SmartieSlave:
    def exposed_tst(self):
        Disconnect(service=self).exec()

    def exposed_cmd(self, name, kwargs_s):
        kwargs = eval(kwargs_s)
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
    rm = ResourceMonitor()
    rm.start()

    with DocXMLRPCServer(('', 8001)) as server_:
        from disco import DiscoClient
        from apparatus import get_my_ip

        dc = DiscoClient()
        dc.announce('SmartieSlave','http://{:s}:{:d}'.format(get_my_ip(),8001))

        server_.register_instance(SmartieSlave())
        os.system('systemd-notify --ready')
        server_.serve_forever()