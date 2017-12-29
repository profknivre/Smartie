import os
from json import load
from pathlib import Path
from shutil import rmtree
from unittest import TestCase

from measurements.historian import engrave, extract_run, RUNDIRNAME

cnt = 0

class Testee:
    def __init__(self):
        global cnt
        self.id = id(self)
        self.bathroom_humidity = cnt
        cnt += 1
        for i in range(10):
            setattr(self, 'param_{:02d}'.format(i), i)


class TestExtract_run(TestCase):
    def setUp(self):
        for i in range(10):
            engrave(Testee(), 1000)
        super().setUp()

    def tearDown(self):
        if os.path.exists(RUNDIRNAME):
            rmtree(RUNDIRNAME)
        super().tearDown()

    def test_basic(self):
        extract_run(5)

    def test_count(self):
        MINUTES = 4
        extract_run(MINUTES)
        p = Path(RUNDIRNAME)
        p = list(p.glob('run_*.json'))[0]
        data = load(open(p, 'rt'))
        self.assertAlmostEquals(len(data), MINUTES)
