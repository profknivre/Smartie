from unittest import TestCase

from case.mock import MagicMock

from fanctrl import FanController
from measurements import Measurements


class TestFanController(TestCase):
    def test_turn_on(self):
        # self.fc.measurements.load()
        self.fc.measurements.humidity = 88
        self.fc.measurements.slope = 1
        self.fc.do_stuff()
        self.fc.fan.on.assert_called()

    def test_turn_off(self):
        # self.fc.measurements.load()
        self.fc.measurements.humidity = 58
        self.fc.measurements.slope = 1
        self.fc.do_stuff()
        self.fc.fan.off.assert_called()

    def setUp(self):
        super().setUp()

        self.fan = MagicMock()
        self.fan.on_time = MagicMock(return_value=33)
        self.fan.on = MagicMock()
        self.fan.off = MagicMock()
        self.meas = Measurements()
        self.fc = FanController(self.fan, self.meas)
