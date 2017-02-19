#!/usr/bin/env python
import unittest
import batchpy
import time
import os


# helper class
class testclass(batchpy.Run):
    def run(self,A=1000,B=[]):
        # do something which takes some time and requires some memory
        a = []
        for i in range(A):
            a.append(i)
        
        return {'a':a,'b':B}


# clear result folder
def clear_res():
    folder = '_res'
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
           
        except Exception, e:
            print e    
        
        
        
# run class testing ############################################################    
class TestRun(unittest.TestCase):
    
    def test_create_run_arguments(self):
        batch = batchpy.Batch(name='testbatch')
        
        testinstance = testclass(batch,B=[1,2,3])
        self.assertEqual(testinstance.parameters,{'A':1000,'B':[1,2,3]})
        
    def test_create_run_id(self):
        batch = batchpy.Batch(name='testbatch')
        
        testinstance1 = testclass(batch)
        testinstance2 = testclass(batch,A=2)
        
        self.assertNotEqual(testinstance1.id,testinstance2.id)
        
    def test_create_run_id_function(self):
        batch = batchpy.Batch(name='testbatch')
        
        def funA(x):
            return x
            
        def funB(x):
            return 2*x
            
        testinstance1 = testclass(batch,A=2,B=funA)
        
        self.assertEqual(testinstance1.id,'9775c501a22ccaf216f2cf3b5498ecb42693cbcd')
        
        
    def test_create_run_id_bytes(self):
        batch = batchpy.Batch(name='testbatch')
     
        testinstance1 = testclass(batch,A=2,B=bytearray.fromhex('deadbeef'))
        
        self.assertEqual(testinstance1.id,'2499831338ca5dc8c44f3d063e076799bea9bdff')
 
        
    def test_create_equal_run(self):
        batch = batchpy.Batch(name='testbatch')
        
        testinstance1 = testclass(batch,A=20)
        testinstance2 = testclass(batch,A=20)
        
        self.assertEqual(testinstance1.id,testinstance2.id)
    
    def test_run_run(self):
        batch = batchpy.Batch(name='testbatch')
        
        testinstance = testclass(batch,saveresult=False,A=100)
        
        res = testinstance()
        self.assertEqual(res,{'a':range(100),'b':[]})
    
    
    
    
    
# batch class testing ##########################################################
class TestBatch(unittest.TestCase):

    def test_create_batch(self):
        name = 'testbatch'
        batch = batchpy.Batch(name=name)
        self.assertEqual(batch.name, name)
        self.assertEqual(batch.run, [])

    def test_add_run(self):
    
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(testclass,{})
        
        self.assertEqual(batch.run[0].parameters,{'A':1000,'B':[]})
    
    def test_add_runs(self):
    
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(testclass,{'A':1})
        batch.add_run(testclass,{'A':2})
        
        self.assertEqual(batch.run[0].parameters,{'A':1,'B':[]})
        self.assertEqual(batch.run[1].parameters,{'A':2,'B':[]})
        
    def test_add_runs_index(self):
    
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(testclass,{'A':1})
        batch.add_run(testclass,{'A':2})
        
        self.assertEqual(batch.run[0].index,0)
        self.assertEqual(batch.run[1].index,1)
            
    def test_add_factorial_runs(self):
    
        batch = batchpy.Batch(name='testbatch')
        batch.add_factorial_runs(testclass,{'A':[1,2,3],'B':[[1,2],[3,4]]})
        
        self.assertEqual(batch.run[0].parameters,{'A':1,'B':[1,2]})
        self.assertEqual(batch.run[1].parameters,{'A':1,'B':[3,4]})
        self.assertEqual(batch.run[2].parameters,{'A':2,'B':[1,2]})
        self.assertEqual(batch.run[3].parameters,{'A':2,'B':[3,4]})
        self.assertEqual(batch.run[4].parameters,{'A':3,'B':[1,2]})
        self.assertEqual(batch.run[5].parameters,{'A':3,'B':[3,4]})

    def test_get_runs_with_eq(self):  
        batch = batchpy.Batch(name='testbatch')
        batch.add_factorial_runs(testclass,{'A':[1,2,3],'B':[[1,2],[3,4]]})
        
        runs = batch.get_runs_with(A=1)
        self.assertIn(batch.run[0],runs)
        self.assertIn(batch.run[1],runs)
        self.assertEqual(len(runs),2)
        
    def test_get_runs_with_ne(self):  
        batch = batchpy.Batch(name='testbatch')
        batch.add_factorial_runs(testclass,{'A':[1,2,3],'B':[[1,2],[3,4]]})
        
        runs = batch.get_runs_with(A__ne=1)
        self.assertIn(batch.run[2],runs)
        self.assertIn(batch.run[3],runs)
        self.assertIn(batch.run[4],runs)
        self.assertIn(batch.run[5],runs)
        self.assertEqual(len(runs),4)
        
    def test_get_runs_with_ge_eq(self):  
        batch = batchpy.Batch(name='testbatch')
        batch.add_factorial_runs(testclass,{'A':[1,2,3],'B':[[1,2],[3,4]]})
        
        runs = batch.get_runs_with(A__ge=2,B=[1,2])
        self.assertIn(batch.run[2],runs)
        self.assertIn(batch.run[4],runs)
        self.assertEqual(len(runs),2)
        
    def test_run(self):
    
        clear_res()
        
        batch = batchpy.Batch(name='testbatch',saveresult=False)
        batch.add_run(testclass,{'A':10})
        batch.add_run(testclass,{'A':20})
        batch(verbose=0)
        
        res = batch.run[0].load()
        self.assertEqual(res,{'a':range(10),'b':[]})
        
        res = batch.run[1].load()
        self.assertEqual(res,{'a':range(20),'b':[]})
        
    def test_run_save(self):
        
        clear_res()
        
        batch = batchpy.Batch(name='testbatch',saveresult=True)
        batch.add_run(testclass,{'A':1000})
        batch.add_run(testclass,{'A':2000})
        batch(verbose=0)
    
    def test_run_rerun(self):
        
        clear_res()
            
        start1 = time.time()
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(testclass,{'A':100000})
        batch.add_run(testclass,{'A':200000})
        batch(verbose=0)
        end1 = time.time()
            
        start2 = time.time()
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(testclass,{'A':100000})
        batch.add_run(testclass,{'A':200000})
        batch(verbose=0)
        end2 = time.time()
        
        self.assertTrue( (end1-start1) > (end2-start2) )
    
    def test_run_save_load(self):
    
        clear_res()
        
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(testclass,{'A':1000})
        batch.add_run(testclass,{'A':2000})
        batch(verbose=0)
        
        # delete and recreate the batch
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(testclass,{'A':1000})
        batch.add_run(testclass,{'A':2000})
        
        res = batch.run[0].load()
        self.assertEqual(res,{'a':range(1000),'b':[]})
        
        res = batch.run[1].load()
        self.assertEqual(res,{'a':range(2000),'b':[]})
        
    def test_add_resultrun(self):
    
        clear_res()
        
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(testclass,{'A':1000})
        batch.add_run(testclass,{'A':2000})
        batch(verbose=0)
        
        ids = [run.id for run in batch.run]
        
        # delete and recreate the batch
        batch = batchpy.Batch(name='testbatch')
        batch.add_resultrun(ids)
        
        res = batch.run[0].load()
        self.assertEqual(res,{'a':range(1000),'b':[]})
        
        res = batch.run[1].load()
        self.assertEqual(res,{'a':range(2000),'b':[]})
        
    def test_get_runs_with_resultrun(self):  
        clear_res()
        
        batch = batchpy.Batch(name='testbatch')
        batch.add_run(testclass,{'A':1000})
        batch.add_run(testclass,{'A':2000})
        batch(verbose=0)
        
        ids = [run.id for run in batch.run]
        
        # delete and recreate the batch
        batch = batchpy.Batch(name='testbatch')
        batch.add_resultrun(ids)
        
        runs = batch.get_runs_with(A__ge=1500)
        self.assertIn(batch.run[1],runs)
        self.assertEqual(len(runs),1)
          
          
if __name__ == '__main__':
    unittest.main()