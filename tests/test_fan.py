from unittest import TestCase
from unittest.mock import MagicMock, patch

from fan import Fan


class TestFan(TestCase):
    def setUp(self):
        super().setUp()
        self.db = dict()
        self.fan = Fan(gpio_pin=MagicMock(), database=self.db)

    def tearDown(self):
        super().tearDown()

    def test_on(self):
        self.fan.gpio_pin.setOutput = MagicMock()
        self.fan.on()
        self.assertIn('on_time', self.db)
        self.fan.gpio_pin.setOutput.assert_called_once_with(1)

    def test_on_off(self):
        self.fan.gpio_pin.setOutput = MagicMock()
        self.fan.on()
        self.fan.gpio_pin.setOutput.assert_called_with(1)
        self.fan.gpio_pin.getInput = MagicMock(return_value=1)
        self.fan.off()
        self.assertNotIn('on_time', self.db)
        self.fan.gpio_pin.setOutput.assert_called_with(0)
        self.assertIn('on_time_last', self.db)
        # print(self.db)

    def test_is_on(self):
        self.fan.gpio_pin.getInput = MagicMock(return_value=1)
        self.assertEqual(1, self.fan.is_on())
        self.fan.gpio_pin.getInput = MagicMock(return_value=0)
        self.assertEqual(0, self.fan.is_on())

    @patch('fan.time')
    def test_on_time(self, time_mock):
        t1 = 1
        t2 = 10
        td = t2 - t1

        self.assertEqual(self.fan.on_time(), 0)
        time_mock.return_value = t1
        self.fan.on()
        self.fan.gpio_pin.getInput = MagicMock(return_value=1)
        time_mock.return_value = t2
        self.assertEqual(self.fan.on_time(), td)

    @patch('fan.time')
    def test_on_time_last(self, time_mock):
        t1 = 1
        t2 = 10
        td = t2 - t1
        time_mock.return_value = t1
        self.fan.on()
        self.fan.gpio_pin.getInput = MagicMock(return_value=1)
        time_mock.return_value = t2
        self.fan.off()
        self.assertEqual(self.fan.on_time_last(), td)
