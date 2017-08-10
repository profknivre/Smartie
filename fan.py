import shelve
from datetime import timedelta
from time import time

from gpio import GPIOBase
from gpio import SysfsGPIO


class Fan:
    def __init__(self, gpio_pin=GPIOBase()):
        self.gpio_pin = gpio_pin

    def on(self):
        self.gpio_pin.setOutput(1)

    def off(self):
        if self.is_on():
            self.gpio_pin.setOutput(0)

    def is_on(self) -> bool:
        return self.gpio_pin.getInput() == 1


class TimedFan(Fan):
    def __init__(self, gpio_pin=GPIOBase(),database=dict()):
        super().__init__(gpio_pin)
        self.db = database

    def on(self, who=None):
        on_time = self.db.get('on_time', time())
        super().on()
        self.db['on_time'] = on_time
        if who is not None:
            self.db['who_on'] = who
        self.db['when_on'] = time()
        if 'off_time' in self.db:
            del self.db['off_time']

    def off(self, who=None):
        if self.is_on():
            self.db['on_time_last'] = self.on_time()
            self.db['off_time'] = time()
            if who is not None:
                self.db['who_off'] = who
            self.db['when_off'] = time()
            del self.db['on_time']
            super().off()

    def on_time(self):
        if not self.is_on():
            return 0
        on_time = self.db.get('on_time', time())
        retval = time() - on_time
        return int(retval)

    def on_time_last(self):
        return self.db.get('on_time_last', 0)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='fiddle with FAN')
    parser.add_argument('val', metavar='val', type=int, nargs='?', help='value', default=None, choices=(0, 1))
    args = parser.parse_args()

    gp = SysfsGPIO(pinnumber=13)
    if gp.getDDR() == gp.DDR_INPUT:
        gp.setDDR(gp.DDR_OUTPUT)

    database = shelve.open('/tmp/fan_data')

    fan = TimedFan(gp, database)

    if (args.val is None):  # read
        ison = fan.is_on()
        if ison:
            print('Fan on for: {}'.format(timedelta(seconds=int(fan.on_time()))))
        else:
            print('Fan is off')

    if (args.val == 1):  # start
        fan.on('manual_ovveride')

    if (args.val == 0):  # stop
        fan.off('manual_ovveride')

    database.close()


if __name__ == '__main__':
    main()
