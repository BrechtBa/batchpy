import unittest
import batchpy

class TestRun(unittest.TestCase):
	
	def test_create_run_arguments(self):
		batch = batchpy.Batch(name='testbatch')

		class testclass(batchpy.Run):
			def create(self,A=1,B=[]):
				pass
		
		testinstance = testclass(batch,B=[1,2,3])
		self.assertEqual(testinstance.parameters,{'A':1,'B':[1,2,3]})

	def test_create_run_id(self):
		batch = batchpy.Batch(name='testbatch')
		class testclass(batchpy.Run):
			def create(self,A=1,B=[]):
				pass
		
		testinstance1 = testclass(batch)
		testinstance2 = testclass(batch,A=2)
		
		self.assertNotEqual(testinstance1.id,testinstance2.id)
	
	def test_create_equal_run(self):
		batch = batchpy.Batch(name='testbatch')
		class testclass(batchpy.Run):
			def create(self,A=1,B=[]):
				pass
		
		testinstance1 = testclass(batch,A=2)
		testinstance2 = testclass(batch,A=2)
		
		self.assertEqual(testinstance1.id,testinstance2.id)
	

class TestBatch(unittest.TestCase):

	def test_create_batch(self):
		name = 'testbatch'
		batch = batchpy.Batch(name=name)
		self.assertEqual(batch.name, name)
		self.assertEqual(batch.run, [])
		self.assertEqual(batch.rundone, [])

	def test_add_run(self):
	
		class testclass(batchpy.Run):
			def create(self,A=1,B=[]):
				pass
		
		batch = batchpy.Batch(name='testbatch')
		batch.add_run(testclass,{})
		
		self.assertEqual(batch.run[0]['runclass'],testclass)
		self.assertEqual(batch.run[0]['parameters'],{})
	
	def test_add_runs(self):
	
		class testclass(batchpy.Run):
			def create(self,A=1,B=[]):
				pass
		
		batch = batchpy.Batch(name='testbatch')
		batch.add_run(testclass,{'A':1})
		batch.add_run(testclass,{'A':2})
		
		self.assertEqual(batch.run[0]['parameters'],{'A':1})
		self.assertEqual(batch.run[1]['parameters'],{'A':2})
		
	def test_add_factorial_runs(self):
	
		class testclass(batchpy.Run):
			def create(self,A=1,B=[]):
				pass
				
		batch = batchpy.Batch(name='testbatch')
		batch.add_factorial_runs(testclass,{'A':[1,2,3],'B':[[1,2],[3,4]]})
		
		self.assertEqual(batch.run[0]['parameters'],{'A':1,'B':[1,2]})
		self.assertEqual(batch.run[1]['parameters'],{'A':1,'B':[3,4]})
		self.assertEqual(batch.run[2]['parameters'],{'A':2,'B':[1,2]})
		self.assertEqual(batch.run[3]['parameters'],{'A':2,'B':[3,4]})
		self.assertEqual(batch.run[4]['parameters'],{'A':3,'B':[1,2]})
		self.assertEqual(batch.run[5]['parameters'],{'A':3,'B':[3,4]})

		
	def test_run(self):
		class testclass(batchpy.Run):
			def create(self,A=1,B=[]):
				pass
			
		batch = batchpy.Batch(name='testbatch')
		batch.add_run(testclass,{'A':1})
		batch.add_run(testclass,{'A':2})
		
		batch()
		
	def test_run_save(self):
		class testclass(batchpy.Run):
			def create(self,A=1,B=[]):
				pass
			
			def execute(self):
				return {'test':self.parameters['A']*2.}
				
		batch = batchpy.Batch(name='testbatch',saveresult=True)
		batch.add_run(testclass,{'A':1})
		batch.add_run(testclass,{'A':2})
		
		batch()
	
	def test_run_save_load(self):
		class testclass(batchpy.Run):
			def create(self,A=1,B=[]):
				pass
			
			def execute(self):
				return {'test':self.parameters['A']*2.}
				
		batch = batchpy.Batch(name='testbatch',saveresult=True)
		batch.add_run(testclass,{'A':1})
		batch.add_run(testclass,{'A':2})
	
		batch()
		
		# delete and recreate the batch
		batch = batchpy.Batch(name='testbatch',saveresult=True)
		batch.add_run(testclass,{'A':1})
		batch.add_run(testclass,{'A':2})
		
		run = batch.get(0)
		self.assertEqual(run.res,{'test':2.})
		
		run = batch.get(1)
		self.assertEqual(run.res,{'test':4.})
		
		
# def test_isupper(self):
# self.assertTrue('FOO'.isupper())
# self.assertFalse('Foo'.isupper())

# def test_split(self):
# s = 'hello world'
# self.assertEqual(s.split(), ['hello', 'world'])
# # check that s.split fails when the separator is not a string
# with self.assertRaises(TypeError):
  # s.split(2)

		  
		  
if __name__ == '__main__':
    unittest.main()