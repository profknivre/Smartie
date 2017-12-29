from unittest import TestCase
from unittest.mock import MagicMock



from conditions.low_humidity_small_slope_condition import LowHumiditySmallSlopeCondition
from measurements import Measurements

from tests import MeasurementMock

mea = MeasurementMock()  # speedup tests

class TestLowHumiditySmallSlope(TestCase):
    def test_handle_nostop(self):
        self.meas.bathroom_humidity = 78
        self.meas.bathroom_humidity_slope = -1

        bool(self.cond)
        self.fan.off.assert_not_called()

    def test_handle_nostop2(self):
        self.meas.bathroom_humidity = 28
        self.meas.bathroom_humidity_slope = -1

        bool(self.cond)
        self.fan.off.assert_not_called()

    def test_handle_stop(self):
        self.meas.bathroom_humidity = 58
        self.meas.bathroom_humidity_slope = 0.51
        self.fan.on_time = MagicMock(return_value=6000)

        bool(self.cond)
        self.fan.off.assert_called()

    def setUp(self):
        super().setUp()
        self.fan = MagicMock()
        self.fan.off = MagicMock()
        self.meas = mea
        self.cond = LowHumiditySmallSlopeCondition(self.fan, self.meas)
