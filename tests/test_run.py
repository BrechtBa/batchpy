#!/usr/bin/env python
import unittest
import batchpy
import numpy as np

from .common import clear_res, MyRun


class TestRun(unittest.TestCase):
    def test_create_run_arguments(self):
        batch = batchpy.Batch(name='testbatch')

        testinstance = MyRun(batch, B=[1, 2, 3])
        self.assertEqual(testinstance.parameters, {'A': 1000, 'B': [1, 2, 3], 'C': np.mean})

    def test_create_run_id(self):
        batch = batchpy.Batch(name='testbatch')

        testinstance1 = MyRun(batch)
        testinstance2 = MyRun(batch, A=2)

        self.assertNotEqual(testinstance1.id, testinstance2.id)

    def test_create_run_id_equal(self):
        batch = batchpy.Batch(name='testbatch')

        testinstance1 = MyRun(batch, A=2.)
        testinstance2 = MyRun(batch, A=2.0000000000)

        self.assertEqual(testinstance1.id, testinstance2.id)

    def test_create_run_id_function(self):
        batch = batchpy.Batch(name='testbatch')

        def rms(x):
            return np.mean(np.array(x) ** 2) ** 0.5

        testinstance1 = MyRun(batch, A=2, C=rms)

        self.assertEqual(testinstance1.id, '785c2581752f58e9877a01b1ba9d8911c017c2fe')

    def test_create_equal_run(self):
        batch = batchpy.Batch(name='testbatch')

        testinstance1 = MyRun(batch, A=20)
        testinstance2 = MyRun(batch, A=20)

        self.assertEqual(testinstance1.id, testinstance2.id)

    def test_run_run(self):
        clear_res()
        batch = batchpy.Batch(name='testbatch')
        testinstance = MyRun(batch, saveresult=False, A=100)

        res = testinstance()

        self.assertEqual(res, {'a': list(range(100)), 'b': [], 'c': np.mean(list(range(100)))})

    def test_run_load(self):
        clear_res()
        batch = batchpy.Batch(name='testbatch')
        testinstance = MyRun(batch, saveresult=True, A=100)
        testinstance()
        res = testinstance.result

        self.assertEqual(res, {'a': list(range(100)), 'b': [], 'c': np.mean(list(range(100)))})

    def test_run_load_function(self):
        batch = batchpy.Batch(name='testbatch')

        def rms(x):
            return np.mean(np.array(x) ** 2) ** 0.5

        testinstance = MyRun(batch, saveresult=True, A=100, C=rms)
        testinstance()
        res = testinstance.result

        self.assertEqual(res, {'a': list(range(100)), 'b': [], 'c': rms(list(range(100)))})


if __name__ == '__main__':
    unittest.main()
