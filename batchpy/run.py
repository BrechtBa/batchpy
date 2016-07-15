#!/usr/bin/env python
import os
import numpy as np
import hashlib
import types
import inspect


class Run(object):
    def __init__(self,batch,saveresult=True,**parameters):
        """
        creates a run
        
        Arguments:
            batch:        batch, the batch the run belongs to
            saveresult: boolean, save the results to disk or not, if not the result is available in the _result attribute
            parameters: other keyword parameters
        """
        
        self.batch = batch
        self._saveresult = saveresult
        self._result = None
        
        # get the parameters from the run function
        self.parameters = {}
        a = inspect.getargspec(self.run)
        for key,val in zip(a.args[-len(a.defaults):],a.defaults):
            self.parameters[key] = val
        
        for key,val in parameters.iteritems():
            self.parameters[key] = val
        
        
        # create the run id
        self.set_id(self.parameters)
        
        # check if there is a retuls saved
        self.check_result()

        
    def run(self,**parameters):
        """
        redefine this method in a child class to define the run
        """
        return {}
        
    def __call__(self):
        if not self.done:
            res = self.run(**self.parameters)
            if self._saveresult:
                np.save(self._filename(),{'res':res,'id':self.id})
            else:
                self._result = res
            
            self.done = True
        else:
            if self._saveresult:
                res = self.load()
            else:
                res = self._result
        return res
        
    def _filename(self):
        return os.path.join(self.batch.savepath() , '{}_{}.npy'.format(self.batch.name,self.id))
        
    def load(self):
        """
        tries to return the run results
        """
        
        try:
            if self._saveresult:
                data = np.load(self._filename())
                res = data.item()['res']
                return res
            else:
                return self._result
        except:
            return None
            
    def clear(self):
        """
        tries to delete the result file from the disk
        """
        try:
            os.remove(self._filename())
            self.done = False
            return True
        except:
            return False
            
    def set_id(self,parameters):
        """
        function creates an id hash from the parameters
        """
        
        id_dict = {}
        for key in parameters.keys():
            c0 = isinstance(parameters[key],types.BooleanType)
            c1 = isinstance(parameters[key],types.IntType)
            c2 = isinstance(parameters[key],types.LongType)
            c3 = isinstance(parameters[key],types.FloatType)
            c4 = isinstance(parameters[key],types.ComplexType)
            c5 = isinstance(parameters[key],types.StringType)
            c6 = isinstance(parameters[key],types.UnicodeType)
            c7 = isinstance(parameters[key],types.TupleType)
            c8 = isinstance(parameters[key],types.ListType)
            c9 = isinstance(parameters[key],types.DictType)
            
            if c1 or c2 or c3 or c4 or c5 or c6 or c7 or c8 or c9:
                id_dict[key] = parameters[key]
                
            elif isinstance(parameters[key],types.FunctionType):
                id_dict[key] = parameters[key].__name__                
            elif isinstance(parameters[key],(type, types.ClassType)):
                id_dict[key] = parameters[key].__name__
            elif isinstance(parameters[key],types.MethodType):
                id_dict[key] = parameters[key].__name__
                
                
        self.id = hashlib.sha1(str([ id_dict[key] for key in id_dict.keys() ])).hexdigest()
        return self.id
    
    def check_result(self):
        # check if there are results saved with the same id
        if os.path.isfile(self._filename()):
            self.done = True
        else:
            self.done = False