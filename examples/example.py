import batchpy


class example_run(batchpy.Run):
	
	def run(self,A=0,B='test'):
	
		self.par = {'A':A,
					'B':B}
		
		print(self.par)
		res = {'val': 'result: {}, {}'.format(self.par['A'],self.par['B'])}
		
		return res


batch = batchpy.Batch('example')

batch.add_factorial_runs( example_run,
                         {'A': [1,2,3],
						  'B': ['test1', 'test2']})
						  
print([run.done for run in batch.run])

batch()

