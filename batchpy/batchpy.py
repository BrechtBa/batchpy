#!/usr/bin/python
import os
import re
import numpy as np
import itertools
import time
import hashlib
import types

class Batch(object):

	def __init__(self,name,path=''):
	
		self.name = name
		self.path = path
		
		self._run = []
		self._rundone = []
		#self.id = []
		
		
	def add_run(self,runclass,parameters):
		"""
		Adds a run
		
		Inputs:
		runclass: a class reference which creates an object when supplied the parameters
		parameters: a dictionary of parameters to be supplied to the init function of the runclass
		
		Example:
		batch.add_run(Cal,{'A':1,'B':[1,2,3],'C':'spam'})
		batch()
		# will run cal() and store the return of cal() in batch.res[] after completion
		# the run will be assigned an id according to cal.id
		"""
		
		self._run.append({'runclass':runclass,'parameters':parameters})
		self._rundone.append(False)
		
	def add_factorial_runs(self,runclass,parameters):
		"""
		Adds runs 
		
		Arguments:
		runcreator: function which returns a run object given a set of input parameters
		inputs: dict with input names and a list of values
		
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
		
		valslist = list(itertools.product(*parameters.values()))
		
		for vals in valslist:
			par = {key:val for key,val in zip(parameters.keys(),vals)}
			self.add_run(runclass,par)

	# def save(self,run=None):
		# """
		# saves the result and the current run index in a file in 'current directory/_res/name.pyz' or 'current directory/_res/name_run_"id".pyz'
		# """
		
		# if self.saveresult:
			# dirname = self._savepath()
			# if self.saverunsseparately:
				# index = self.id.index(run.id)
				# filename = os.path.join(dirname , self.name + '_run{}'.format(index))
				# np.save(filename,{'rundone':[self.rundone[index]],'res':[self.run[index].res],'id':[self.id[index]]})
			# else:
				# filename = os.path.join(dirname , self.name)
				# np.save(filename,{'rundone':self.rundone,'res':[run.res for run in self.run],'id':self.id})
		
	# def load(self,idx):
		# """
		# check if the idx is in the loaded id's and assign the results if so
		# """
		
		# for rundone,res,id in zip(self._temprundone,self._tempres,self._tempid):
			# if self.id[idx] == id:
				# self.rundone[idx] = rundone
				# self.run[idx].res.update(res)
			
	# def get_res(self,key):
		# """
		# returns a list of results for all res
		
		# Arguments:
		# key: a key in the res dict
		# """
		# return [ run.res[key] for run in self.run]
		
	def __call__(self,runind=-1):
		"""
		runs the remainder of the batch or a specified run
		"""
		title_width = 80
		
		#check which runs are to be done
		runs = []
		
		
		if isinstance(runind,list):
			for ind in runind:
				if not self._rundone[ind]:
					runs.append(ind)
		else:		
			if runind < 0:
				for ind in range(len(self._run)):
					if not self._rundone[ind]:
						runs.append(ind)
						
			elif not self._rundone[runind]:
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
			

			
			runclass = self._run[run]['runclass']
			parameters = self._run[run]['parameters']
			runinstance = runclass(self,parameters)
			
			# run the run
			runinstance()
			
			# set the current run to done
			self._rundone[run] = True
			
			
		# if not self.saveeveryrun and len(runs)>0:
			# self.save()
		
		runtime = time.time()-starttime
		print('total runtime {0:.1f} min'.format(runtime/60))
		print('done')
		
	def _savepath(self):
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
		Returns a list of found files which should be loaded
		"""
		
		dirname = self._savepath()
		filenames = []
		if self.saverunsseparately:
			files = [f for f in os.listdir(dirname) if re.match(self.name+r'_run.*\.npy', f)]
			for f in files:
				filenames.append( os.path.join(dirname , f) )
		else:
			filename = os.path.join(dirname , self.name + '.npy')
			if os.path.isfile(filename):
				filenames.append(filename)
				
		return filenames
	
	
class Run(object):
	def __init__(self,batch,parameters,autosave=False):
		"""
		creates a run instance
		"""
		
		self.batch = batch
		
		self._parameters = parameters
		self._id = self.set_id()
		self._autosave = autosave
		
		# make sure there is a res dictionary
		self.res = {}
		
		self.create(**parameters)
		
		# load results if they exits
		self.load()
		
	def create(self,**parameters):
		"""
		redefine this method in a child class to define the run
		the method is run during the initiation of a new object with the 
		instance parameters as keyword arguments
		"""
		pass
		
	def __call__(self):	
		self.execute()
		
		if self._autosave:
			self.save()
		
	def execute(self):
		"""
		redefine this method in a child class to define the run
		the method is run during the execution of the batch 
		"""
		pass
		
	def _filename(self):
		return os.path.join(self.batch.savepath , '{}_run{}'.format(self.batch.name,self._id))
		
	def save(self):
		"""
		saves the run results
		"""
		
		np.save(self._filename(),{'res':self.res,'id':self._id})
		
	def load(self):
		"""
		tries to load the run results
		"""
		
		try:
			data = np.load(self._filename())
			self.res = data['res']
		except:
			pass
				
	def set_id(self):
		"""
		function creates an id hash from the parameters
		"""
		
		# remove the self object from the dictionary
		id_dict = dict(self._parameters)
		if 'self' in id_dict:
			del id_dict['self']
		
		# replace all classes with their name as they are redefined on each startup
		for key in id_dict.keys():
			if isinstance(id_dict[key],types.ClassType):
				id_dict[key] = id_dict[key].__name__
				
		self.id = hashlib.sha1(str([ id_dict[key] for key in id_dict.keys() ])).hexdigest()
		
		
# helper functions
def strlist(runs):
	if len(runs) > 5:
		return '[' + str(runs[0]) + ',' + str(runs[1]) + ',...,' + str(runs[-2]) + ',' + str(runs[-1]) +']'
	else:
		return str(runs)