from unittest import TestCase
from unittest.mock import MagicMock

from conditions import LowHumiditySmallSlopeCondition
from measurements import Measurements


class TestLowHumiditySmallSlope(TestCase):
    def test_handle_nostop(self):
        self.meas.humidity = 78
        self.meas.slope = -1

        self.cond()
        self.fan.off.assert_not_called()

    def test_handle_nostop2(self):
        self.meas.humidity = 28
        self.meas.slope = -1

        self.cond()
        self.fan.off.assert_not_called()

    def test_handle_stop(self):
        self.meas.humidity = 58
        self.meas.slope = 0.51
        self.fan.on_time = MagicMock(return_value=600)

        self.cond()
        self.fan.off.assert_called()

    def setUp(self):
        super().setUp()
        self.fan = MagicMock()
        self.fan.off = MagicMock()
        self.meas = Measurements()
        self.cond = LowHumiditySmallSlopeCondition(self.fan, self.meas)
