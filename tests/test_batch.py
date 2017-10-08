#!/usr/bin/env python
import unittest
import batchpy
import time
import numpy as np

from .common import MyRun, clear_res


class TestBatch(unittest.TestCase):
    def test_create_batch(self):
        name = 'testbatch'
        batch = batchpy.Batch(name=name)

        self.assertEqual(batch.name, name)
        self.assertEqual(batch.run, [])

    def test_add_run(self):
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(MyRun, {})

        self.assertEqual(batch.run[0].parameters, {'A': 1000, 'B': None, 'C': np.mean})

    def test_add_runs(self):
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(MyRun, {'A': 1})
        batch.add_run(MyRun, {'A': 2})

        self.assertEqual(batch.run[0].parameters, {'A': 1, 'B': None, 'C': np.mean})
        self.assertEqual(batch.run[1].parameters, {'A': 2, 'B': None, 'C': np.mean})

    def test_add_runs_index(self):
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(MyRun, {'A': 1})
        batch.add_run(MyRun, {'A': 2})

        self.assertEqual(batch.run[0].index, 0)
        self.assertEqual(batch.run[1].index, 1)

    def test_add_factorial_runs(self):
        batch = batchpy.Batch(name='testbatch')
        batch.add_factorial_runs(MyRun, {'A': [1, 2, 3], 'B': [[1, 2], [3, 4]]})

        runs = [
            {'par': {'A': 1, 'B': [1, 2], 'C': np.mean}, 'found': False},
            {'par': {'A': 1, 'B': [3, 4], 'C': np.mean}, 'found': False},
            {'par': {'A': 2, 'B': [1, 2], 'C': np.mean}, 'found': False},
            {'par': {'A': 2, 'B': [3, 4], 'C': np.mean}, 'found': False},
            {'par': {'A': 3, 'B': [1, 2], 'C': np.mean}, 'found': False},
            {'par': {'A': 3, 'B': [3, 4], 'C': np.mean}, 'found': False},
        ]
        for r in runs:
            for run in batch.run:
                if run.parameters == r['par']:
                    r['found'] = True
                    break

        for r in runs:
            self.assertTrue(r['found'])

    def test_add_factorial_runs_string(self):

        batch = batchpy.Batch(name='testbatch')
        batch.add_factorial_runs(MyRun, {'A': [1, 2, 3], 'B': [[1, 2], [3, 4]], 'C': 'test'})

        runs = [
            {'par': {'A': 1, 'B': [1, 2], 'C': 'test'}, 'found': False},
            {'par': {'A': 1, 'B': [3, 4], 'C': 'test'}, 'found': False},
            {'par': {'A': 2, 'B': [1, 2], 'C': 'test'}, 'found': False},
            {'par': {'A': 2, 'B': [3, 4], 'C': 'test'}, 'found': False},
            {'par': {'A': 3, 'B': [1, 2], 'C': 'test'}, 'found': False},
            {'par': {'A': 3, 'B': [3, 4], 'C': 'test'}, 'found': False},
        ]
        for r in runs:
            for run in batch.run:
                if run.parameters == r['par']:
                    r['found'] = True
                    break

        for r in runs:
            self.assertTrue(r['found'])

    def test_add_factorial_runs_single_value(self):

        batch = batchpy.Batch(name='testbatch')
        batch.add_factorial_runs(MyRun, {'A': [1, 2, 3], 'B': [[1, 2], [3, 4]], 'C': 1.})

        runs = [
            {'par': {'A': 1, 'B': [1, 2], 'C': 1.}, 'found': False},
            {'par': {'A': 1, 'B': [3, 4], 'C': 1.}, 'found': False},
            {'par': {'A': 2, 'B': [1, 2], 'C': 1.}, 'found': False},
            {'par': {'A': 2, 'B': [3, 4], 'C': 1.}, 'found': False},
            {'par': {'A': 3, 'B': [1, 2], 'C': 1.}, 'found': False},
            {'par': {'A': 3, 'B': [3, 4], 'C': 1.}, 'found': False},
        ]
        for r in runs:
            for run in batch.run:
                if run.parameters == r['par']:
                    r['found'] = True
                    break

        for r in runs:
            self.assertTrue(r['found'])

    def test_get_runs_with_eq(self):
        batch = batchpy.Batch(name='testbatch')
        batch.add_factorial_runs(MyRun, {'A': [1, 2, 3], 'B': [[1, 2], [3, 4]]})

        runs = batch.get_runs_with(A=1)
        for run in batch.run:
            if run.parameters['A'] == 1:
                self.assertIn(run, runs)
            else:
                self.assertNotIn(run, runs)

    def test_get_runs_with_ne(self):
        batch = batchpy.Batch(name='testbatch')
        batch.add_factorial_runs(MyRun, {'A': [1, 2, 3], 'B': [[1, 2], [3, 4]]})

        runs = batch.get_runs_with(A__ne=1)
        for run in batch.run:
            if run.parameters['A'] == 1:
                self.assertNotIn(run, runs)
            else:
                self.assertIn(run, runs)

    def test_get_runs_with_ge_eq(self):
        batch = batchpy.Batch(name='testbatch')
        batch.add_factorial_runs(MyRun, {'A': [1, 2, 3], 'B': [[1, 2], [3, 4]]})

        runs = batch.get_runs_with(A__ge=2, B=[1, 2])
        for run in batch.run:
            if run.parameters['A'] >= 2 and run.parameters['B'] == [1, 2]:
                self.assertIn(run, runs)
            else:
                self.assertNotIn(run, runs)

    def test_run(self):
        clear_res()
        batch = batchpy.Batch(name='testbatch', saveresult=False)
        batch.add_run(MyRun, {'A': 10})
        batch.add_run(MyRun, {'A': 20})
        batch(verbose=0)

        res = batch.run[0].result
        self.assertEqual(res, {'a': list(range(10)), 'b': [], 'c': np.mean(list(range(10)))})

        res = batch.run[1].result
        self.assertEqual(res, {'a': list(range(20)), 'b': [], 'c': np.mean(list(range(20)))})

    def test_run_async(self):
        clear_res()
        batch = batchpy.Batch(name='testbatch', saveresult=False, processes=4)
        batch.add_run(MyRun, {'A': 10})
        batch.add_run(MyRun, {'A': 20})
        batch(verbose=0)

        res = batch.run[0].result
        self.assertEqual(res, {'a': list(range(10)), 'b': [], 'c': np.mean(list(range(10)))})

        res = batch.run[1].result
        self.assertEqual(res, {'a': list(range(20)), 'b': [], 'c': np.mean(list(range(20)))})

    def test_run_save(self):
        clear_res()
        batch = batchpy.Batch(name='testbatch', saveresult=True)
        batch.add_run(MyRun, {'A': 1000})
        batch.add_run(MyRun, {'A': 2000})
        batch(verbose=0)

    def test_run_rerun(self):
        clear_res()
        start1 = time.time()
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(MyRun, {'A': 100000})
        batch.add_run(MyRun, {'A': 200000})
        batch(verbose=0)
        end1 = time.time()

        start2 = time.time()
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(MyRun, {'A': 100000})
        batch.add_run(MyRun, {'A': 200000})
        batch(verbose=0)
        end2 = time.time()

        self.assertTrue((end1 - start1) > (end2 - start2))

    def test_run_save_load(self):
        clear_res()
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(MyRun, {'A': 1000})
        batch.add_run(MyRun, {'A': 2000})
        batch(verbose=0)

        # delete and recreate the batch
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(MyRun, {'A': 1000})
        batch.add_run(MyRun, {'A': 2000})

        res = batch.run[0].result
        self.assertEqual(res, {'a': list(range(1000)), 'b': [], 'c': np.mean(list(range(1000)))})

        res = batch.run[1].result
        self.assertEqual(res, {'a': list(range(2000)), 'b': [], 'c': np.mean(list(range(2000)))})

    def test_run_save_load_async(self):
        clear_res()
        batch = batchpy.Batch(name='testbatch', processes=4)
        batch.add_run(MyRun, {'A': 1000})
        batch.add_run(MyRun, {'A': 2000})
        batch(verbose=0)

        # delete and recreate the batch
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(MyRun, {'A': 1000})
        batch.add_run(MyRun, {'A': 2000})

        res = batch.run[0].result
        self.assertEqual(res, {'a': list(range(1000)), 'b': [], 'c': np.mean(list(range(1000)))})

        res = batch.run[1].result
        self.assertEqual(res, {'a': list(range(2000)), 'b': [], 'c': np.mean(list(range(2000)))})

    def test_add_resultrun(self):
        clear_res()
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(MyRun, {'A': 1000})
        batch.add_run(MyRun, {'A': 2000})
        batch(verbose=0)

        ids = [run.id for run in batch.run]

        # delete and recreate the batch
        batch = batchpy.Batch(name='testbatch')
        batch.add_resultrun(ids)

        res = batch.run[0].result
        self.assertEqual(res, {'a': list(range(1000)), 'b': [], 'c': np.mean(list(range(1000)))})

        res = batch.run[1].result
        self.assertEqual(res, {'a': list(range(2000)), 'b': [], 'c': np.mean(list(range(2000)))})

    def test_add_resultrun_function(self):
        clear_res()

        def rms(x):
            return np.mean(np.array(x) ** 2) ** 0.5

        batch = batchpy.Batch(name='testbatch')
        batch.add_run(MyRun, {'A': 1000, 'C': rms})
        batch.add_run(MyRun, {'A': 2000, 'C': rms})
        batch(verbose=0)

        rms0 = rms(range(1000))
        rms1 = rms(range(2000))

        del rms

        ids = [run.id for run in batch.run]

        # delete and recreate the batch
        batch = batchpy.Batch(name='testbatch')
        batch.add_resultrun(ids)

        self.assertEqual(batch.run[0].parameters, {'A': 1000, 'B': None, 'C': 'rms'})
        self.assertEqual(batch.run[1].parameters, {'A': 2000, 'B': None, 'C': 'rms'})

        res = batch.run[0].result
        self.assertEqual(res, {'a': list(range(1000)), 'b': [], 'c': rms0})

        res = batch.run[1].result
        self.assertEqual(res, {'a': list(range(2000)), 'b': [], 'c': rms1})

    def test_get_runs_with_resultrun(self):
        clear_res()
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(MyRun, {'A': 1000})
        batch.add_run(MyRun, {'A': 2000})
        batch(verbose=0)

        ids = [run.id for run in batch.run]

        # delete and recreate the batch
        batch = batchpy.Batch(name='testbatch')
        batch.add_resultrun(ids)

        runs = batch.get_runs_with(A__ge=1500)
        self.assertIn(batch.run[1], runs)
        self.assertEqual(len(runs), 1)

    def test_save_ids(self):
        clear_res()
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(MyRun, {'A': 1000})
        batch.add_run(MyRun, {'A': 2000})
        old_ids = [run.id for run in batch.run]

        batch.save_ids()

        ids = list(np.load('_res/testbatch_ids.npy'))

        self.assertEqual(ids, old_ids)

    def test_save_ids_py(self):
        clear_res()
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(MyRun, {'A': 1000})
        batch.add_run(MyRun, {'A': 2000})
        old_ids = [run.id for run in batch.run]

        batch.save_ids(format='py')

        from _res.testbatch_ids import ids
        self.assertEqual(ids, old_ids)


if __name__ == '__main__':
    unittest.main()
