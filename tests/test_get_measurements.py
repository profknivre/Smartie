from unittest import TestCase

MEASUREMENTS = frozenset(['Dht', 'OnlineWeather', 'Ds18', 'CoreTemp'])


class TestGet_measurements(TestCase):
    def test_get_measurements(self):
        from measurements.factory import get_measurements

        _measurements = list(get_measurements())
        _measurements = list(map(lambda x: x.__name__, _measurements))
        _measurements = set(_measurements)

        self.assertEqual(_measurements, MEASUREMENTS, 'missing measurements ?')

    def setUp(self):
        import sys
        mods = map(str, sys.modules)
        mods = reversed(list(filter(lambda x: 'measureme' in x, mods)))

        def delete_module(a):
            del sys.modules[a]

        list(map(delete_module, list(mods)))
