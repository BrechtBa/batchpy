#!/usr/bin/env python
# batchPy
# Documentation
import os
import numpy as np

class Batch():

	def __init__(self,path,name):
	
		self.path = path
		self.name = name
		self.run = []
		self.res = []
		self.currentrun = 0
		
	def add_run(self,run,res):
		"""
		Inputs:
		run a callable object which runs whatever needs to be run
		res a link to a dict where the results of run are stored
		
		example:
		batch.add_run(cal,cal.res)
		"""
		
		self.run.append(run)
		self.res.append(res)
		self.load(len(self.run)-1)
		
	def clear_run(self,run):
		self.currentrun = run
		if len(self.res) > run:
			self.res[run].clear()

	def save(self):
		"""
		saves the result and the currentrun index in a file in 'curent directory/data/name.pyz' 
		"""

		filename = self._savepath()
		
		np.savez(filename,self.currentrun,self.res)
		
	def load(self,run):
		"""
		check is there is a file with the appropriate name in 'curent directory/data/name.pyz'
		and loads the data and currentrun index from it
		"""

		filename = self._savepath()
		
		if os.path.isfile(filename):
			temp = np.load(filename)
			self.currentrun = temp['arr_0'].item()
			res = temp['arr_1']
			
			if len(res) > run:
				self.res[run].update(res[run])
					
	def __call__(self,run=-1):
		"""
		runs the remainder of the batch or a specified run
		"""
		title_width = 60
		
		if run >= 0:
			if isinstance(run,list):
				runs = run
			else:
				runs = [run]
		else:
			runs = range(self.currentrun, len(self.run))
		
		for i in runs:
			print(title_width*'#')
			print('###   run %s / %s  ' % (self.currentrun+1,len(self.run)) + (title_width-19-len(str(self.currentrun+1))-len(str(len(self.run))))*' ' +' ###' )
			print(title_width*'#')
			print(' ')
			
			runobj = self.run[i]
			runobj()
			if run >= 0:
				self.currentrun = i+1
			
			self.save()
			print(' ')
			
	def _savepath(self):
		dirname = os.path.join(self.path, '_data' )
		filename = os.path.join(dirname , self.name +'.npz' )
		
		if not os.path.isdir(dirname):
			os.makedirs(dirname)
			
		return filename