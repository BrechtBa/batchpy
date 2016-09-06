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

import os
import hashlib
import types
import inspect
import time
import numpy as np

class Run(object):
    """
    A batchpy run base class        
    
    This class is intended as a base class from which custom user defined run
    objects can inherit.
    In the custom run class the :code:`run` method needs to be redefined to
    actually run the wanted computations and return the result as a dictionary.
    
    Examples
    --------
    >>> class myrun(batchpy.Run):
    ...     def run(self,mypar=5):
    ...         # some conplicated computation
    ...         return {'val': 2*mypar}
    ...
    >>> batch = batchpy.Batch('mybatch')
    >>> run = myrun(batch,saveresult=False,mypar=5)
    >>> run()
    {'val': 10}
    
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
        
        Examples
        --------
        >>> batch = batchpy.Batch('mybatch')
        >>> run = myrun(batch,saveresult=False,mypar=5)
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

        
    def run(self):
        """
        Perform calculations and return the result
        
        This method should be overwritten in a user defined child class to
        perform the actual computations.
        
        Parameters
        ----------
        parameters
            parameters can be defined as named parameters. The use of **kwargs is
            not supported.
        
        Returns
        -------
        res : dict
            a dictionary with the results of the run
            
        Examples
        --------
        >>> class myrun(batchpy.Run):
        ...     def run(self,mypar=5):
        ...         # some conplicated computation
        ...         return {'val': 2*mypar}
        ...
        
        """

        return {}
        
    def __call__(self):
        """
        Checks if the run results are allready computed and compute them if not.
        
        When a run is called the class checks if the results are available in
        memory or on the disk.
        
        When the result is available in memory, it is
        returned. When it is available on disk, it is loaded and returned.
        
        When the result is not available it is computed using the :code:`run`
        method and the results are stored on disk (if the :code:`_saveresult`
        attribute is true) or in the :code:`_result` attribute (otherwise).
        
        The computation is timed and the runtime is saved in the :code:`runtime`
        attribute.
  
        Returns
        -------
        res : dict
            results dictionary
            
        Examples
        --------
        >>> run()
        {'val': 10}
        
        """
        
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
        """
        Returns the filename of the run
        
        """
        return os.path.join(self.batch.savepath() , '{}_{}.npy'.format(self.batch.name,self.id))
        
    def load(self):
        """
        Checks if the run results are allready computed and return them if so.
        
        When the result is available in memory, it is
        returned. When it is available on disk, it is loaded and returned.
        When the result is not computed yet this returns :code:`None`
        
        Returns
        -------
        res : dict, :code:`None`
            results dictionary. return :code:`None` if the results are not
            available

        Examples
        --------
        >>> run.load()
        {'val': 10}
        
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
        Tries to erase the run results from the disk
        
        Returns
        -------
        success : bool
            :code:`True` if the run was deleted from the disk, :code:`False`
            otherwise

        Examples
        --------
        >>> run.clear()
        True
        
        """
        
        try:
            os.remove(self._filename())
            self.done = False
            return True
        except:
            return False
            
    def set_id(self,parameters):
        """
        Creates an id hash from the parameters
        
        The id hash is used to identify a run. It is hashed from the parameters
        used to create the run to ensure that when even a single parameter is
        changed the run ids are different. The id is stored in the :code`id`
        attribute.
        
        Parameters
        ----------
        parameters : dict
            a dictionary with parameters from which to compute the hash
        
        Returns
        -------
        id : string
            the id hash of this run

        Notes
        -----
        When classes, methods or functions are supplied as parameters, the hash
        is created using their name attribute. This avoids ids being different
        when python is restarted. A hash created from the function itself would 
        be different each time python starts as the object resides in a
        different memory location.
        
        Examples
        --------
        >>> run.set_id(run.parameters)
        '10ae24979c5028fa873651bca338152dc0484245'
        
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
        """
        Checks if a result file is stored on the disk
       
        Checks if a file with the correct name can be found. Is so, it sets the 
        :code:`done` attribute to True. If not, the :code:`done` attribute is
        set to false.
        
        Examples
        --------
        >>> run.check_result()
        >>> run.done
        False
        
        """
        
        # check if there are results saved with the same id
        if os.path.isfile(self._filename()):
            self.done = True
        else:
            self.done = False
            