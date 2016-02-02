#!/usr/bin/python
import os
import numpy as np
import hashlib
import types
import inspect

class Run(object):
	def __init__(self,batch,saveresult=True,**parameters):
		"""
		creates a run instance
		"""
		
		self.batch = batch
		
		self.parameters = {}
		a = inspect.getargspec(self.create)
		for key,val in zip(a.args[-len(a.defaults):],a.defaults):
			self.parameters[key] = val
		
		for key,val in parameters.iteritems():
			self.parameters[key] = val
		
		self.set_id()
		
		self._saveresult = saveresult
		
		# make sure there is a res dictionary
		self.res = {}
		
		# run the create function
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
		self.res = self.execute()
		
		if self._saveresult:
			self.save()
		
	def execute(self):
		"""
		redefine this method in a child class to define the run
		the method is run during the execution of the batch 
		"""
		return {}
		
	def _filename(self):
		return os.path.join(self.batch.savepath() , '{}_{}.npy'.format(self.batch.name,self.id))
		
	def save(self):
		"""
		saves the run results
		"""
		
		np.save(self._filename(),{'res':self.res,'id':self.id})
		
	def load(self):
		"""
		tries to load the run results
		"""
		
		try:
			data = np.load(self._filename())
			self.res = data.item()['res']
			return True
			
		except:
			return False
				
	def set_id(self):
		"""
		function creates an id hash from the parameters
		"""
		
		id_dict = {}
		for key in self.parameters.keys():
			c0 = isinstance(self.parameters[key],types.BooleanType)
			c1 = isinstance(self.parameters[key],types.IntType)
			c2 = isinstance(self.parameters[key],types.LongType)
			c3 = isinstance(self.parameters[key],types.FloatType)
			c4 = isinstance(self.parameters[key],types.ComplexType)
			c5 = isinstance(self.parameters[key],types.StringType)
			c6 = isinstance(self.parameters[key],types.UnicodeType)
			c7 = isinstance(self.parameters[key],types.TupleType)
			c8 = isinstance(self.parameters[key],types.ListType)
			c9 = isinstance(self.parameters[key],types.DictType)
			
			if c1 or c2 or c3 or c4 or c5 or c6 or c7 or c8 or c9:
				id_dict[key] = self.parameters[key]
				
			elif isinstance(self.parameters[key],types.FunctionType):
				id_dict[key] = self.parameters[key].__name__				
			elif isinstance(self.parameters[key],types.ClassType):
				id_dict[key] = self.parameters[key].__name__
			elif isinstance(self.parameters[key],types.MethodType):
				id_dict[key] = self.parameters[key].__name__
		
		
		# remove the self object from the dictionary
		# id_dict = dict(self.parameters)
		# if 'self' in id_dict:
			# del id_dict['self']
		
		# # replace all classes and functions with their name as they are redefined on each startup
		# for key in id_dict.keys():
			# if isinstance(id_dict[key],types.ClassType):
				# id_dict[key] = id_dict[key].__name__
			
			# elif isinstance(id_dict[key],types.FunctionType):
				# id_dict[key] = id_dict[key].__name__
				
			# elif isinstance(id_dict[key],types.InstanceType):
				# del id_dict[key]
				
			# elif isinstance(id_dict[key],types.MethodType):
				# id_dict[key] = id_dict[key].__name__
				
		
		self.id = hashlib.sha1(str([ id_dict[key] for key in id_dict.keys() ])).hexdigest()
	