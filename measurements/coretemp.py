import logging
from subprocess import check_output

from measurements.base_measurement import BaseMeasurement

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class CoreTemp(BaseMeasurement):
    def read(self):
        try:
            return float(
                check_output(['/opt/vc/bin/vcgencmd', 'measure_temp'])
                    .decode('utf8').strip()[5:].replace("'C", ''))
        except Exception as e:
            log.error(e)
            return 0


class RemoteCoreTemp(CoreTemp):
    def read(self):
        cn = self.conn
        retval = cn.root.exposed_cmd('read_coretemp', **vars(self))
        return retval
