from unittest import TestCase

# REGRESSION...!!!

CONDITIONS = frozenset((
    'LowHumiditySmallSlopeCondition',
    'LongRunningTimeCondition',
    'ForceStopCondition',
    'HighHumidityAndHighSlopeCondition',
    'ForceStartCondition'))


class TestGet_condition_list(TestCase):
    def test_get_condition_list(self):
        from conditions import get_condition_list

        cnds = list(get_condition_list())
        cnds = list(map(lambda x: x.__name__, cnds))
        cnds = set(cnds)

        self.assertEqual(cnds, CONDITIONS, 'missing conditions ?')

    def setUp(self):
        import sys
        mods = map(str, sys.modules)
        mods = reversed(list(filter(lambda x: 'Condition' in x, mods)))

        def delete_module(a):
            del sys.modules[a]

        list(map(delete_module, list(mods)))
