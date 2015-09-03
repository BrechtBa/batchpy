#!/usr/bin/env python
# batchPy
# Documentation
import os
import numpy as np
import itertools
import time
import hashlib
import types

class Batch():

	def __init__(self,name,path=''):
	
		self.name = name
		self.path = path
		
		self.run = []
		self.res = []
		self.id = []
		self.rundone = []
		
		self.saveeveryrun = True
		
		# check if there are results saved with the same name and load them
		filename = self._savepath()
		if os.path.isfile(filename):
			temp = np.load(filename)
			self._temprundone = temp['arr_0']
			self._tempres = temp['arr_1']
			self._tempid = temp['arr_2']
		else:
			self._temprundone = []
			self._tempres = []
			self._tempid = []
		
	def add_run(self,run,id=None):
		"""
		Adds a run
		
		Inputs:
		run: a callable object which runs whatever needs to be run and can have an attribute id when no id attribute is present the index will be the id

		Example:
		batch.add_run(cal)
		batch()
		# will run cal() and store the return of cal() in batch.res[] after completion
		# the run will be assigned an id according to cal.id
		"""
		
		self.run.append(run)
		self.res.append({})
		if id == None:
			if hasattr(run, 'id'):
				self.id.append(run.id)
			else:
				self.id.append( len(self.id) )
		else:
			print('use of separate id argument is depreciated, include the id as an attribute of the run')
			self.id.append(id)
		self.rundone.append(False)
		
		# check if there are results for a run with this hash and load it if so
		self.load(len(self.run)-1)
		
	def add_factorial_runs(self,runcreator,inputs,res='res',par='par'):
		"""
		Adds runs 
		
		Arguments:
		runcreator: function which returns a run objects and an id given a set of input parameters
		inputs: dict with input names and a list of values
		res: a string reference to a results attribute of the run object
		par: a string reference to a parameters attribute of the run object used to identify the run
		
		Example:
		batch.add_factorial_runs(createcal,{'par1':[0,1,2],'par2':[5.0,7.1]})
		# is equivalent with:
		batch.add_run(createcal(par1=0,par2=5.0))
		batch.add_run(createcal(par1=1,par2=5.0))
		batch.add_run(createcal(par1=2,par2=5.0))
		batch.add_run(createcal(par1=0,par2=7.1))
		batch.add_run(createcal(par1=1,par2=7.1))
		batch.add_run(createcal(par1=2,par2=7.1))
		"""
		
		valslist = list(itertools.product(*inputs.values()))
		
		for vals in valslist:
			input = {key:val for key,val in zip(inputs.keys(),vals)}
			run,id = runcreator(**input)
			self.add_run(run,id)
		
	def clear_run(self,run):
		self.currentrun = run
		if len(self.res) > run:
			self.res[run].clear()

	def save(self):
		"""
		saves the result and the currentrun index in a file in 'curent directory/_res/name.pyz' 
		"""

		filename = self._savepath()
		
		np.savez(filename,self.rundone,self.res,self.id)
		
	def load(self,idx):
		"""
		check if the idx is in the loaded id's and assign the results if so
		"""
		
		for rundone,res,id in zip(self._temprundone,self._tempres,self._tempid):
			if self.id[idx] == id:
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
			

			
			runobj = self.run[run]
			
			# update the res attribute
			self.res[run] = runobj()
			
			# set the current run to done
			self.rundone[run] = True
			
			if self.saveeveryrun:
				self.save()
		
		if not self.saveeveryrun and len(runs)>0:
			self.save()
		
		runtime = time.time()-starttime
		print('total runtime {0:.1f} min'.format(runtime/60))
		print('done')
		
	def _savepath(self):
		dirname = os.path.join(self.path, '_res' )
		filename = os.path.join(dirname , self.name +'.npz' )
		
		if not os.path.isdir(dirname):
			os.makedirs(dirname)
			
		return filename
		
class Run():
	def set_id(self,d):
		"""
		function creates an id hash from a dictionary
		Arguments:
		
		"""
		# remove the self object from the dictionary
		id_dict = dict(d)
		if 'self' in id_dict:
			del id_dict['self']
		
		# replace all classes with their name as they are redefined on each startup
		for key in id_dict.keys():
			if isinstance(id_dict[key],types.ClassType):
				id_dict[key] = id_dict[key].__name__
				
		
		self.id = hashlib.sha1(str([ id_dict[key] for key in id_dict.keys() ])).hexdigest()
		self.id_dict = id_dict
		
# helper functions
def strlist(runs):
	if len(runs) > 5:
		return '[' + str(runs[0]) + ',' + str(runs[1]) + ',...,' + str(runs[-2]) + ',' + str(runs[-1]) +']'
	else:
		return str(runs)