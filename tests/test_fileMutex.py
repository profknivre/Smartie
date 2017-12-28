from unittest import TestCase
from util import FileMutex
from contextlib import suppress
import os

fname = '/tmp/test_Filemutex'


class TestFileMutex(TestCase):
    def test_basic(self):
        with FileMutex(fname=fname):
            pass

    def test_locked(self):
        f = open(fname, 'x')
        f.close()

        with self.assertRaises(FileExistsError):
            with FileMutex(fname=fname):
                self.fail("No wai!!")

    def test_locked_remains(self):
        f = open(fname, 'x')
        f.close()

        with suppress(FileExistsError):
            with FileMutex(fname=fname):
                self.fail("No wai!!")

        with self.assertRaises(FileExistsError):
            with FileMutex(fname=fname):
                self.fail("No wai!!")

    def setUp(self):
        with suppress(FileNotFoundError):
            os.unlink(fname)
        super().setUp()

    def tearDown(self):
        with suppress(FileNotFoundError):
            os.unlink(fname)


super().tearDown()