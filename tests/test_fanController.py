from unittest import TestCase

from case.mock import MagicMock

from fanctrl import FanController
from measurements import Measurements

# TODO: make it more reasonable!!!

mea = Measurements()  # speedup tests

class TestFanController(TestCase):
    def test_turn_on(self):
        # self.fc.measurements.load()
        self.fc.measurements.bathroom_humidity = 88
        self.fc.measurements.bathroom_humidity_slope = 1
        self.fan.is_on = MagicMock(return_value=False)
        self.fc.do_stuff()
        self.fc.fan.on.assert_called()

    def test_turn_off(self):
        # self.fc.measurements.load()
        self.fc.measurements.bathroom_humidity = 58
        self.fc.measurements.bathroom_humidity_slope = 1
        self.fan.is_on = MagicMock(return_value=True)
        self.fc.do_stuff()
        self.fc.fan.off.assert_called()

    def setUp(self):
        super().setUp()

        self.fan = MagicMock()
        self.fan.on_time = MagicMock(return_value=3300)
        self.fan.on = MagicMock()
        self.fan.off = MagicMock()
        self.meas = mea
        self.fc = FanController(self.fan, self.meas)
