#!/usr/bin/env python
import os
import numpy as np
import hashlib
import types
import inspect
#!/usr/bin/env/ python
################################################################################
#    Copyright (c) 2016 Brecht Baeten
#    This file is part of batchpy.
#    
#    Permission is hereby granted, free of charge, to any person obtaining a
#    copy of this software and associated documentation files (the "Software"), 
#    to deal in the Software without restriction, including without limitation 
#    the rights to use, copy, modify, merge, publish, distribute, sublicense, 
#    and/or sell copies of the Software, and to permit persons to whom the 
#    Software is furnished to do so, subject to the following conditions:
#    
#    The above copyright notice and this permission notice shall be included in 
#    all copies or substantial portions of the Software.
################################################################################

import time

class Run(object):
    """
    A batchpy run base class        
    
    This class is intended as a base class from which custom user defined run
    objects can inherit.
    In the custom run class the :code:`run` method needs to be redefined to
    actually run the wanted computations and return the result as a dictionary.
    
    Examples
    --------
    >>> class myrun(batchpy.run):
    ...     def run(**parameters):
    ...         return 2*parameters['mypar']
    
    """
    
    def __init__(self,batch,saveresult=True,**parameters):
        """
        Creates a batchpy run
        
        Parameters
        ----------
        batch : batch
            the batch the run belongs to
            
        saveresult : boolean
            save the results to disk or not, if not the result is available
            in the _result attribute
            
        **parameters : 
            keyword parameters which modify the run instance
           
        Notes
        -----
        batchpy runs should not be created directly
        
        """
        
        self.batch = batch
        self.runtime = None
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
            t_start = time.time()
            
            res = self.run(**self.parameters)
            
            t_end = time.time()
            self.runtime = t_end-t_start
            
            if self._saveresult:
                np.save(self._filename(),{'res':res,'id':self.id,'runtime':self.runtime})
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
                
                # try - except statement for compatibility with older saved runs
                try:
                    self.runtime = data.item()['runtime']
                except:
                    pass
                    
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