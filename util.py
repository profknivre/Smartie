import signal

import config


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
        self.timing_caption = kwargs.get('timing_caption', adaptee.timing_caption)
        self.gauge_caption = kwargs.get('gauge_caption', adaptee.gauge_caption)
        UberAdapter.retval[id(self.adaptee)] = None
        super().__init__()

    def read(self):
        if UberAdapter.retval[id(self.adaptee)] is None:
            UberAdapter.retval[id(self.adaptee)] = self.adaptee.read()
        return UberAdapter.retval[id(self.adaptee)][self.index]
