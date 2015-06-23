#!/usr/bin/env python
# batchPy
# Documentation
import os
import numpy as np
import itertools
import time

class Batch():

	def __init__(self,path,name):
	
		self.path = path
		self.name = name
		self.run = []
		self.resname = []
		self.res = []
		self.parname = []
		self.par = []
		self.rundone = []
		
	def add_run(self,run,res='res',par='par'):
		"""
		Adds a run
		
		Inputs:
		run: a callable object which runs whatever needs to be run
		res: a string reference to a results dictionary of the run object
		par: a string reference to a parameters dictionary of the run object used to identify the run
		
		Example:
		batch.add_run(cal,res='results',par='temp.parameters')
		batch()
		# will run cal() and store cal.results in batch.res[0] after completion
		# parameters in cal.temp.parameters will be taken to define the run
		"""
		
		self.run.append(run)
		#self.resname.append(res)
		#self.res.append(multi_getattr(self.run[-1],self.resname[-1]))
		self.res.append({})
		self.parname.append(par)
		self.par.append(multi_getattr(self.run[-1],self.parname[-1]))
		self.rundone.append(False)
		
		# check if there are results for a run with this hash and load it if so
		self.load(len(self.run)-1)
		
	def add_factorial_runs(self,runcreator,inputs,res='res',par='par'):
		"""
		Adds runs 
		
		Arguments:
		runcreator: function which returns run objects given a set of input parameters
		inputs: dict with input names and a list of values
		res: a string reference to a results attribute of the run object
		par: a string reference to a parameters attribute of the run object used to identify the run
		
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
			self.add_run(runcreator(**input),res=res,par=par)
		
	def clear_run(self,run):
		self.currentrun = run
		if len(self.res) > run:
			self.res[run].clear()

	def save(self):
		"""
		saves the result and the currentrun index in a file in 'curent directory/_res/name.pyz' 
		"""

		filename = self._savepath()
		
		np.savez(filename,self.rundone,self.res,self.parname,self.par)
		
	def load(self,idx):
		"""
		check is there is a file with the appropriate name in 'curent directory/_res/name.pyz'
		and loads the data and currentrun index from it
		"""

		filename = self._savepath()
		
		if os.path.isfile(filename):
			temp = np.load(filename)
			rundones = temp['arr_0']
			ress = temp['arr_1']
			parnames = temp['arr_2']
			pars = temp['arr_3']
			
			for rundone,res,parname,par in zip(rundones,ress,parnames,pars):
				if parname == self.parname[idx]:
					# if the parameter attributes of saved and created runs match update the run
					if multi_getattr(self.run[idx],parname) == par:
						self.rundone[idx] = rundone
						self.res[idx].update(res)
				
	def get_res(self,key):
		"""
		returns a list of results for all res
		
		Arguments:
		key: a key in the res dict
		"""
		return [ res[key] for res in self.res]
		
	def __call__(self,run=-1):
		"""
		runs the remainder of the batch or a specified run
		"""
		title_width = 80
		
		#check which runs are to be done
		runs = []
		if run < 0:
			for idx in range(len(self.run)):
				if not self.rundone[idx]:
					runs.append(idx)
		else:
			if isinstance(run,list):
				for idx in run:
					if not self.rundone[idx]:
						runs.append(idx)
			else:
				if not self.rundone[run]:
					runs.append(run)
			
			
		starttime = time.time()
		runcount = 0
		for idx in runs:
			#print(title_width*'#')
			runtime = time.time()-starttime
			if runcount==0:
				etastr = '/'
			else:
				etastr = '%.1f min' % ( runtime/runcount*(len(runs)-runcount)/60 )
			
			runcount += 1
				
			title_str = '###   run %s in ' % (idx)
			title_str += strlist(runs)
			title_str += '       runtime: %.1f min' % (runtime/60)
			title_str += '       eta: '+etastr
			title_str += (title_width-len(title_str)-3)*' ' +'###'
			
			print(title_str)
			#print(title_width*'#')
			
			runobj = self.run[idx]
			#runobj()
			
			# update the res attribute
			self.res[idx] = runobj() #multi_getattr(self.run[idx],self.resname[idx])
			
			# set the current run to done
			self.rundone[idx] = True
			
			self.save()
	
			
	def _savepath(self):
		dirname = os.path.join(self.path, '_res' )
		filename = os.path.join(dirname , self.name +'.npz' )
		
		if not os.path.isdir(dirname):
			os.makedirs(dirname)
			
		return filename
		
		
		
# helper functions
def multi_getattr(obj, attr, default = None):
	"""
	Get a named attribute from an object; multi_getattr(x, 'a.b.c.d') is
	equivalent to x.a.b.c.d. When a default argument is given, it is
	returned when any attribute in the chain doesn't exist; without
	it, an exception is raised when a missing attribute is encountered.

	Example:
	obj  = [1,2,3]
	attr = "append.__doc__.capitalize.__doc__"

	multi_getattr(obj, attr) #Will return the docstring for the
							 #capitalize method of the builtin string
							 #object
	"""
	attributes = attr.split(".")
	for i in attributes:
		try:
			obj = getattr(obj, i)
		except AttributeError:
			if default:
				return default
			else:
				raise
	return obj
        
def strlist(runs):
	if len(runs) > 5:
		return '[' + str(runs[0]) + ',' + str(runs[1]) + '...' + str(runs[-2]) + ',' + str(runs[-1]) +']'
	else:
		return str(runs)