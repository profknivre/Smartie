from unittest import TestCase
from unittest.mock import MagicMock

from conditions import HighHumidityAndHighSlopeCondition
from measurements import Measurements

mea = Measurements()  # speedup tests

class TestHighHumidityRiseCondtion(TestCase):
    def test_handle_run(self):
        self.meas.bathroom_humidity = 88
        self.meas.bathroom_humidity_slope = 1

        self.cond()
        self.fan.on.assert_called()

    def test_handle_notrun1(self):
        self.meas.bathroom_humidity = 78
        self.meas.bathroom_humidity_slope = 1

        self.cond()
        self.fan.on.assert_not_called()

    def test_handle_notrun2(self):
        self.meas.bathroom_humidity = 88
        self.meas.bathroom_humidity_slope = 0.51

        self.cond()
        self.fan.on.assert_not_called()

    def setUp(self):
        super().setUp()
        self.fan = MagicMock()
        self.fan.on = MagicMock()
        self.fan.is_on = MagicMock(return_value=False)
        self.meas = mea
        self.cond = HighHumidityAndHighSlopeCondition(self.fan, self.meas)
