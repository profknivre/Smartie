import contextlib
import time
import logging
import lzma
import os
import signal

import config

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def get_slope(data):
    # y = a*x+b
    a, b = linreg(range(len(data)), data)
    return a


def linreg(x, y):
    """
    return a,b in solution to y = ax + b such that root mean square distance between trend line
    and original points is minimized
    """
    n = len(x)
    sx = sy = sxx = syy = sxy = 0.0
    for x_, y_ in zip(x, y):
        sx = sx + x_
        sy = sy + y_
        sxx = sxx + x_ * x_
        syy = syy + y_ * y_
        sxy = sxy + x_ * y_
    det = sxx * n - sx * sx
    try:
        return (sxy * n - sy * sx) / det, (sxx * sy - sx * sxy) / det
    except ZeroDivisionError:
        return 0, 0


class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


class FileMutex:
    def __init__(self, fname = '/tmp/smartie.mutex'):
        self.fname = fname
        self.f = None

    def __enter__(self):
        # if os.path.exists(self.fname):
        #     raise Exception('already running')
        self.f = open(self.fname,mode='x')
        self.f.write(str(os.getpid()))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.f: self.f.close()
        if os.path.exists(self.fname):
            os.unlink(self.fname)


class TimerMock:
    class timer:
        def __init__(self, caption):
            pass

        def __enter__(self):
            return

        def __exit__(self, type, value, traceback):
            return

        def a(arg):
            pass

    class gauge:
        def __init__(self, caption, val):
            pass


def isQuietTime(current_time):
    if current_time.tm_wday in (5, 6):  # weekend
        if current_time.tm_hour in (config.weekend_quiet_hours):
            return True
    return False


class UberAdapter:
    """
    singletonizer ??
    """

    retval = {}

    def __init__(self, adaptee, index, **kwargs):
        self.adaptee = adaptee
        self.index = index

        if 'timing_caption' in kwargs:
            self.timing_caption = kwargs.get('timing_caption')
        elif hasattr(adaptee, 'timing_caption'):
            self.timing_caption = adaptee.timing_caption

        if 'gauge_caption' in kwargs:
            self.gauge_caption = kwargs.get('gauge_caption')
        elif hasattr(adaptee, 'gauge_caption'):
            self.gauge_caption = adaptee.gauge_caption

        UberAdapter.retval[id(self.adaptee)] = None
        super().__init__()

    def read(self):
        if UberAdapter.retval[id(self.adaptee)] is None:
            UberAdapter.retval[id(self.adaptee)] = self.adaptee.read()
        return UberAdapter.retval[id(self.adaptee)][self.index]


class RemoteAdapter:
    def __init__(self, adaptee, **kwargs):
        vars(self).update(kwargs)
        self.adaptee = adaptee

    def read(self):
        cn = self.conn
        dct = dict(filter(lambda x: not x[0] in ('conn', 'adaptee'), vars(self).items()))
        retval = cn.exposed_cmd(self.adaptee.REMOTE_CMD, repr(dct))
        return retval


class ResourceMonitor:
    def __init__(self, **kwargs):
        from  threading import Thread
        vars(self).update(kwargs)
        self.stats = config.stats_client
        self.monitoring = config.enable_resource_monitoring
        self.hosts = config.resource_monitor_hosts
        self.worker_thread = Thread(target=self.worker, name=kwargs.get('name', 'ResourceMonitor'), daemon=True)

    def start(self):
        self.worker_thread.start()

    def worker(self):
        import psutil
        from platform import node
        from time import sleep

        hostname = node().replace('.lan', '')

        if hostname in self.hosts:
            while True:
                pvm = psutil.virtual_memory()
                fields = ('used')  # , 'free')
                nfo = dict(filter(lambda x: x[0] in fields, zip(pvm._asdict(), pvm)))

                for k in nfo.keys():
                    caption = '{}.memory.{}'.format(hostname, k)
                    if self.monitoring:
                        self.stats.gauge(caption, nfo.get(k))
                        # print(caption, nfo.get(k))
                sleep(60)


def XZRotator(source, dest):
    """
    Move and xz rotator
    """
    f_in = open(source, 'rb')
    f_out = lzma.open(dest, 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()
    os.remove(source)


def XZNamer(default_name):
    return default_name+'.xz'


class Stats:
    @staticmethod
    @contextlib.contextmanager
    def timer(subname: str):
        """Returns a context manager to time execution of a block of code.

        >>> with stats.timer('context_timer'):
        ...     # resulting timer name: context_timer
        ...     pass
        """

        _start = _last = time.time()
        # enter
        yield
        # exit
        _stop = time.time()

        delta = _stop - _start

        log.info(f'{subname} delta {delta}')
        # b exit

    @staticmethod
    def gauge(caption, val):
        log.info(f'{caption}:{val}')
