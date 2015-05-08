# batchPy
# Documentation
import os
import numpy as np

class Batch():

	def __init__(self,path,name):
	
		self.path = path
		self.name = name
		self.runs = []
		self.result = []
		self.currentrun = 0
		
	def add_run(self,run):
		"""
		Inputs:
		run a callable object which runs whatever needs to be run and returns a dict with results to append to data
		"""
		self.runs.append(run)
		self.result.append({})
		self.load(len(self.runs)-1)
		
	def clear_run(self,run):
		self.currentrun = run
		if len(self.result) > run:
			self.result[run] = {}
			if 'result' in dir(self.runs[run]):
				self.runs[run].result = {}
	
	def save(self):
		"""
		saves the result and the currentrun index in a file in 'curent directory/data/name.pyz' 
		"""

		filename = self._savepath()
		
		np.savez(filename,self.currentrun,self.result)
		
	def load(self,run):
		"""
		check is there is a file with the appropriate name in 'curent directory/data/name.pyz'
		and loads the data and currentrun index from it
		"""

		filename = self._savepath()
		
		if os.path.isfile(filename):
			temp = np.load(filename)
			self.currentrun = temp['arr_0'].item()
			result = temp['arr_1']
			
			if len(result) > run:
				self.result[run] = result[run]
				if 'result' in dir(self.runs[run]):
					self.runs[run].result = result[run]
					
			
	
	def __call__(self):
		"""
		runs the remainder of the batch
		"""
		
		while self.currentrun < len(self.runs):
			print('#####################################' )
			print('###   run %s                       ###' % self.currentrun )
			print('#####################################' )
			print(' ')
			
			run = self.runs[self.currentrun]
			self.result[self.currentrun] = run()
			self.currentrun += 1
			
			self.save()
	
	def _savepath(self):
		dirname = os.path.join(self.path, '_data' )
		filename = os.path.join(dirname , self.name +'.npz' )
		
		if not os.path.isdir(dirname):
			os.makedirs(dirname)
			
		return filename