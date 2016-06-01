#!/usr/bin/env python
import os
import re
import numpy as np
import itertools
import time

class Batch(object):

	def __init__(self,name,path='',saveresult=True):
		"""
		creates a batch
		
		Parameters:
		name:			string, a name for the batch
		path:			string, a optional path to store results, if not provided the current path is chosen
		saveresult: 	boolean, save the results to disk or not, this argument is passed to all runs
		"""
		
		self.name = name
		self.path = path
		
		self.run = []
		self._saveresult = saveresult
		
	def add_run(self,runclass,parameters):
		"""
		Adds a run
		
		Parameters:
		runclass: 		a class reference which creates an object when supplied the parameters
		parameters: 	a dictionary of parameters to be supplied to the init function of the runclass
		
		Example:
		batch.add_run(Cal,{'A':1,'B':[1,2,3],'C':'spam'})
		batch()
		# will run cal() and store the return of cal() in batch.res[] after completion
		# the run will be assigned an id according to cal.id
		"""
		
		self.run.append(runclass(self,saveresult=self._saveresult,**parameters))
		
	def add_factorial_runs(self,runclass,parameters):
		"""
		Adds runs 
		
		Parameters:
		runcreator: function which returns a run object given a set of input parameters
		inputs: dict with input names and a list of values
		
		Example:
		batch.add_factorial_runs(createcal,{'par1':[0,1,2],'par2':[5.0,7.1]})
		# is equivalent with:
		batch.add_run(createcal(par1=0,par2=5.0))
		batch.add_run(createcal(par1=0,par2=7.1))
		batch.add_run(createcal(par1=1,par2=5.0))
		batch.add_run(createcal(par1=1,par2=7.1))
		batch.add_run(createcal(par1=2,par2=5.0))
		batch.add_run(createcal(par1=2,par2=7.1))
		"""
		
		valslist = list(itertools.product(*parameters.values()))
		
		for vals in valslist:
			par = {key:val for key,val in zip(parameters.keys(),vals)}
			self.add_run( runclass,par )
			
		
	def __call__(self,runind=-1):
		"""
		runs the remainder of the batch or a specified run
		
		Parameters:
		runind:			int or list of ints, indices of the runs to be executed, -1 for all runs
		"""
		title_width = 80
		
		#check which runs are to be done
		runs = []
		
		
		if isinstance(runind,list):
			for ind in runind:
				if not self.run[ind].done:
					runs.append(ind)
		else:		
			if runind < 0:
				for ind in range(len(self.run)):
					if not self.run[ind].done:
						runs.append(ind)
						
			elif not self.run[runind].done:
				runs.append(runind)
	

		skip = int( np.ceil( len(runs)/50. ) )
			
		starttime = time.time()
		for i,run in enumerate(runs):
			
			# print the run title string
			if i%skip==0:
				runtime = time.time()-starttime
				if i==0:
					etastr = '/'
				else:
					etastr = '{0:.1f} min'.format( runtime/i*(len(runs)-i)/60 )
					
				title_str = '### run {0} in '.format(run)
				title_str += strlist(runs)
				title_str += (40-len(title_str))*' '
				title_str += 'runtime: {0:.1f} min'.format(runtime/60)
				title_str += 4*' '
				title_str += 'eta: '+etastr
				title_str += (title_width-len(title_str)-3)*' ' +'###'
				print(title_str)
			

			# run the run
			self.run[run]()
		
		runtime = time.time()-starttime
		print('total runtime {0:.1f} min'.format(runtime/60))
		print('done')
		
	def savepath(self):
		"""
		Returns the path where files are saved
		"""
		dirname = os.path.join(self.path, '_res' )
		filename = os.path.join(dirname , self.name )
		
		if not os.path.isdir(dirname):
			os.makedirs(dirname)
		
		return dirname
	
	def _get_filenames(self):
		"""
		Returns a list of found files which correspond to the batch
		"""
		
		dirname = self.savepath()
		filenames = []
		files = [f for f in os.listdir(dirname) if re.match(self.name+r'_run.*\.npy', f)]
		for f in files:
			filenames.append( os.path.join(dirname , f) )
				
		return filenames
	
# helper functions
def strlist(runs):
	if len(runs) > 5:
		return '[' + str(runs[0]) + ',' + str(runs[1]) + ',...,' + str(runs[-2]) + ',' + str(runs[-1]) +']'
	else:
		return str(runs)