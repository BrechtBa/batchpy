#!/usr/bin/env python
# batchPy
# Documentation
import os
import numpy as np
import itertools

class Batch():

	def __init__(self,path,name):
	
		self.path = path
		self.name = name
		self.run = []
		self.resname = []
		self.res = []
		self.currentrun = 0
		
	def add_run(self,run,res='res'):
		"""
		Adds a run
		
		Inputs:
		run: a callable object which runs whatever needs to be run
		res: a string to a results attribute of the run object
		
		Example:
		batch.add_run(cal,res='results')
		batch()
		# will run cal() and store cal.results in batch.res[0] after completion
		"""
		
		self.run.append(run)
		self.resname.append(res)
		self.res.append(getattr(self.run[-1],self.resname[-1]))
		self.load(len(self.run)-1)
		
	def add_factorial_runs(self,runcreator,inputs,res='res'):
		"""
		Adds runs 
		
		Arguments:
		runcreator: function which returns run objects given a set of input parameters
		inputs: dict with input names and a list of values
		res: a string to a results attribute of the run object
		
		Example:
		batch.add_factorial_runs(createcal,{'par1':[0,1,2],'par2':[5.0,7.1]},res='results')
		# is equivalent with:
		batch.add_run(createcal(par1=0,par2=5.0),res='results')
		batch.add_run(createcal(par1=1,par2=5.0),res='results')
		batch.add_run(createcal(par1=2,par2=5.0),res='results')
		batch.add_run(createcal(par1=0,par2=7.1),res='results')
		batch.add_run(createcal(par1=1,par2=7.1),res='results')
		batch.add_run(createcal(par1=2,par2=7.1),res='results')
		"""
		
		valslist = list(itertools.product(*inputs.values()))
		
		for vals in valslist:
			input = {key:val for key,val in zip(inputs.keys(),vals)}
			self.add_run(runcreator(**input),res=res)
		
	def clear_run(self,run):
		self.currentrun = run
		if len(self.res) > run:
			self.res[run].clear()

	def save(self):
		"""
		saves the result and the currentrun index in a file in 'curent directory/_res/name.pyz' 
		"""

		filename = self._savepath()
		
		np.savez(filename,self.currentrun,self.res)
		
	def load(self,run):
		"""
		check is there is a file with the appropriate name in 'curent directory/_res/name.pyz'
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
		title_width = 80
		
		if run < 0:
			runs = range(self.currentrun, len(self.run))
		else:
			if isinstance(run,list):
				runs = run
			else:
				runs = [run]
			
		
		for i in runs:
			#print(title_width*'#')
			title_str = '###   run %s / %s' % (self.currentrun,len(runs))
			
			title_str = title_str + (title_width-len(title_str)-3)*' ' +'###'
			
			print(title_str)
			#print(title_width*'#')
			print(' ')
			
			runobj = self.run[i]
			runobj()
			
			# update the res attribute
			self.res[i] = getattr(self.run[i],self.resname[i])
			
			if run < 0:
				self.currentrun = i+1
			
			self.save()
			print(' ')
			
	def _savepath(self):
		dirname = os.path.join(self.path, '_res' )
		filename = os.path.join(dirname , self.name +'.npz' )
		
		if not os.path.isdir(dirname):
			os.makedirs(dirname)
			
		return filename