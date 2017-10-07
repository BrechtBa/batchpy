#!/usr/bin/env python
import unittest
import batchpy
import time

from .common import clear_res


# the run class used for testing
class LongRun(batchpy.Run):
    def run(self, sleep=60):
        time.sleep(sleep)
        return {'a': 1}


class TestInterrupt(unittest.TestCase):
    def test_interrupt(self):
        clear_res()

        batch = batchpy.Batch(name='testbatch', saveresult=False, processes=4)
        batch.add_run(LongRun, {'sleep': 60})
        batch.add_run(LongRun, {'sleep': 60})
        batch.add_run(LongRun, {'sleep': 60})
        batch.add_run(LongRun, {'sleep': 10})
        batch.add_run(LongRun, {'sleep': 10})
        batch.add_run(LongRun, {'sleep': 10})
        batch()


if __name__ == '__main__':
    unittest.main()
