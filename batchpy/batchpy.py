#!/usr/bin/python
import os
import re
import numpy as np
import itertools
import time
import hashlib
import types

class Batch():

	def __init__(self,name,path='',saveresult=True,saverunsseparately=False,saveeveryrun=True):
	
		self.name = name
		self.path = path
		
		self.run = []
		self.res = []
		self.id = []
		self.rundone = []
		
		self.saveresult = saveresult
		self.saverunsseparately = saverunsseparately
		if self.saverunsseparately:
			self.saveeveryrun = True
		else:
			self.saveeveryrun = saveeveryrun
		
		# check if there are results saved with the same name and load them
		self._temprundone = []
		self._tempres = []
		self._tempid = []
		
		filenames = self._get_filenames()
		for filename in filenames:
			data = np.load(filename)
			
			#	conversion between old and new format co keep compatibility
			if 'arr_0' in data:
				np.savez(filename,rundone=data['arr_0'],res=data['arr_1'],id=data['arr_2'])
				data = np.load(filename)
				
			for rundone,res,id in zip(data['rundone'],data['res'],data['id']):
				self._temprundone.append(rundone)
				self._tempres.append(res)
				self._tempid.append(id)
		
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
			run = runcreator(**input)
			self.add_run(run)
		
	def clear_run(self,run):
		self.currentrun = run
		if len(self.res) > run:
			self.res[run].clear()

	def save(self,run=None):
		"""
		saves the result and the current run index in a file in 'current directory/_res/name.pyz' or 'current directory/_res/name_run_"id".pyz'
		"""
		
		if self.saveresult:
			dirname = self._savepath()
			if self.saverunsseparately:
				index = self.id.index(run.id)
				filename = os.path.join(dirname , self.name + '_run{}.npz'.format(index))
				np.savez(filename,rundone=[self.rundone[index]],res=[self.res[index]],id=[self.id[index]])
			else:
				filename = os.path.join(dirname , self.name + '.npz')
				np.savez(filename,rundone=self.rundone,res=self.res,id=self.id)
		
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
				self.save(runobj)
		
		if not self.saveeveryrun and len(runs)>0:
			self.save()
		
		runtime = time.time()-starttime
		print('total runtime {0:.1f} min'.format(runtime/60))
		print('done')
		
	def _savepath(self):
		"""
		Returns the pathe where files are saved
		"""
		dirname = os.path.join(self.path, '_res' )
		filename = os.path.join(dirname , self.name )
		
		if not os.path.isdir(dirname):
			os.makedirs(dirname)
		
		return dirname
	
	def _get_filenames(self):
		"""
		Returns a list of found files which should be loaded
		"""
		
		dirname = self._savepath()
		filenames = []
		if self.saverunsseparately:
			files = [f for f in os.listdir(dirname) if re.match(self.name+r'_run.*\.npz', f)]
			for f in files:
				filenames.append( os.path.join(dirname , f) )
		else:
			filename = os.path.join(dirname , self.name + '.npz')
			if os.path.isfile(filename):
				filenames.append(filename)
				
		return filenames
	
	
class Run():
	def set_id(self,d):
		"""
		function creates an id hash from a dictionary
		Arguments:
		d:         dictionary
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