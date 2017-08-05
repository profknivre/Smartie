from unittest import TestCase
from unittest.mock import MagicMock

from conditions import HighHumidityAndHighSlopeCondtion
from measurements import Measurements


class TestHighHumidityRiseCondtion(TestCase):
    def test_handle_run(self):
        self.meas.humidity = 88
        self.meas.slope = 1

        self.cond()
        self.fan.on.assert_called()

    def test_handle_notrun1(self):
        self.meas.humidity = 78
        self.meas.slope = 1

        self.cond()
        self.fan.on.assert_not_called()

    def test_handle_notrun2(self):
        self.meas.humidity = 88
        self.meas.slope = 0.51

        self.cond()
        self.fan.on.assert_not_called()

    def setUp(self):
        super().setUp()
        self.fan = MagicMock()
        self.fan.on = MagicMock()
        self.meas = Measurements()
        self.cond = HighHumidityAndHighSlopeCondtion(self.fan, self.meas)
