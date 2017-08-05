from time import time

from gpio import GPIOBase


class Fan:
    def __init__(self, gpio_pin=GPIOBase(), database=dict()):
        self.gpio_pin = gpio_pin
        self.db = database

    def on(self):
        on_time = self.db.get('on_time', time())
        self.gpio_pin.setOutput(1)
        self.db['on_time'] = on_time
        if 'off_time' in self.db:
            del self.db['off_time']

    def off(self):
        if self.is_on():
            self.db['on_time_last'] = self.on_time()
            self.db['off_time'] = time()
            del self.db['on_time']
            self.gpio_pin.setOutput(0)

    def is_on(self) -> bool:
        return self.gpio_pin.getInput() == 1

    def on_time(self):
        if not self.is_on():
            return 0
        on_time = self.db.get('on_time', time())
        retval = time() - on_time
        return retval

    def on_time_last(self):
        return self.db.get('on_time_last', 0)
