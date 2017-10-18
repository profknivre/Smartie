from unittest import TestCase

from util import UberAdapter


class Adaptee:
    readcnt = 0

    def __init__(self):
        self.timing_caption = 'adaptee.timing_caption'
        self.gauge_caption = 'adaptee.gauge_caption'

    def read(self):
        Adaptee.readcnt += 1
        return 'a', 'b'


class TestUberAdapter(TestCase):
    def setUp(self):
        super().setUp()
        Adaptee.readcnt = 0

        self.adaptee = Adaptee()
        self.subject1 = UberAdapter(self.adaptee, 0)
        self.subject2 = UberAdapter(self.adaptee, 1)

    def test_read(self):
        self.assertEqual(self.subject1.read(), 'a')
        self.assertEqual(self.subject2.read(), 'b')
        self.assertEqual(Adaptee.readcnt, 1)
