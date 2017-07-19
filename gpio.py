import os
from abc import abstractmethod


class GPIOBase:
    DDR_OUTPUT = 1
    DDR_INPUT = 0

    DIRs = frozenset((DDR_OUTPUT, DDR_INPUT))

    @abstractmethod
    def setDDR(self, direction):
        pass

    @abstractmethod
    def setOutput(self, value):
        pass

    @abstractmethod
    def getInput(self):
        pass

    @abstractmethod
    def getDDR(self):
        pass


class GPIO(GPIOBase):
    def __init__(self, gp_impl=GPIOBase()):
        self._gp_impl = gp_impl

    def setOutput(self, value):
        gp = self._gp_impl
        if self.getDDR() == GPIOBase.DDR_OUTPUT:
            return gp.setOutput(value)
        else:
            raise Exception("GPIO: trying to force value on input pin")

    def getInput(self):
        gp = self._gp_impl

        # if self.getDDR(pin) == GPIOBase.DDR_INPUT:
        return gp.getInput()
        # else:
        #    raise Exception("GPIO: trying to read value from output pin")

    def setDDR(self, direction):
        gp = self._gp_impl

        if direction in GPIOBase.DIRs:
            return gp.setDDR(direction)
        else:
            raise Exception("GPIO: wrong direction: {0:d}".format(direction))

    def getDDR(self):
        gp = self._gp_impl
        return gp.getDDR()


class SysfsGPIO(GPIOBase):
    def __init__(self, pinnumber=13):
        super().__init__()

        self._pinnumber = pinnumber
        self.prefix = '/sys/class/gpio/'
        self.gpio = 'gpio{}'.format(self._pinnumber)
        self.value_path = '{}{}/value'.format(self.prefix, self.gpio)
        self.direction_path = '{}{}/direction'.format(self.prefix, self.gpio)

        self.dirmap = {self.DDR_INPUT: 'in',
                       self.DDR_OUTPUT: 'out'}

        self.rdirmap = {'in': self.DDR_INPUT,
                        'out': self.DDR_OUTPUT}

        if not os.path.exists(self.value_path):
            with open(self.prefix + 'export', 'w') as file:
                file.write('{}\n'.format(self._pinnumber))

    def setOutput(self, value):
        with open(self.value_path, 'w') as file:
            file.write('{}\n'.format(value))

    def setDDR(self, direction):
        with open(self.direction_path, 'w') as file:
            file.write('{}\n'.format(self.dirmap.get(direction, self.DDR_INPUT)))

    def getDDR(self):
        with open(self.direction_path, 'r') as file:
            val = file.read().strip()
            return self.rdirmap.get(val, self.DDR_INPUT)

    def getInput(self):
        with open(self.value_path, 'r') as file:
            val = int(file.read().strip())
            return val


def Main():
    import argparse

    parser = argparse.ArgumentParser(description='fiddle with gpio')
    parser.add_argument('pin', metavar='pinnum', type=int, nargs='?', help='gpio pin number', default=13)
    parser.add_argument('val', metavar='val', type=int, nargs='?', help='value', default=None, choices=(0, 1))
    parser.add_argument('--ddr', metavar='direction', type=int, nargs=1, help='data direction register', default=None,
                        choices=(0, 1))

    args = parser.parse_args()
    # print(args)

    gp = SysfsGPIO(pinnumber=args.pin)

    if args.ddr != None:
        gp.setDDR(args.ddr)

    if (args.val == None):
        print(gp.getInput())
        return
    else:
        gp.setOutput(args.val)


if __name__ == '__main__':
    Main()
