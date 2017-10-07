#!/usr/bin/env python
import unittest
import batchpy
import numpy as np

from .common import clear_res, MyRun


class TestVarious(unittest.TestCase):
    def test_convert_run_to_newstyle(self):
        clear_res()
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(MyRun, {'A': 1000})
        batch.add_run(MyRun, {'A': 2000})
        batch(verbose=0)

        ids = [run.id for run in batch.run]

        for run in batch.run:
            batchpy.convert_run_to_newstyle(run)

        # delete and recreate the batch
        batch = batchpy.Batch(name='testbatch')
        batch.add_resultrun(ids)

        res = batch.run[0].load()
        self.assertEqual(res, {'a': list(range(1000)), 'b': [], 'c': np.mean(list(range(1000)))})

        res = batch.run[1].load()
        self.assertEqual(res, {'a': list(range(2000)), 'b': [], 'c': np.mean(list(range(2000)))})


if __name__ == '__main__':
    unittest.main()
