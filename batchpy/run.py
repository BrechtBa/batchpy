#!/usr/bin/env/ python
################################################################################
#    Copyright (C) 2016 Brecht Baeten
#    This file is part of batchpy.
#    
#    batchpy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    batchpy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with batchpy.  If not, see <http://www.gnu.org/licenses/>.
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
        self.id = None
        self.done = False
        self.runtime = None
        self._saveresult = saveresult
        self._result = None

        
        # get the parameters from the run function
        self._resultonly = False
        self._parameters = {}
        a = inspect.getargspec(self.run)
        for key,val in zip(a.args[-len(a.defaults):],a.defaults):
            self._parameters[key] = val
        
        for key,val in parameters.iteritems():
            self._parameters[key] = val
        
        
        # create the run id
        self.set_id(self._parameters)
             
        # check if there is a result saved
        self._check_result()

        
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
        Checks if the run results are already computed and compute them if not.
        
        When a run is called the class checks if the results are available in
        memory or on the disk.
        
        When the result is available in memory, it is returned. When it is
        available on disk, it is loaded and returned.
        
        When the result is not available it is computed using the :code:`run`
        method and the results are stored on disk (if the :code:`_saveresult`
        attribute is true) or in the :code:`_result` attribute (otherwise).
        
        The computation is timed and the runtime is saved in the :code:`runtime`
        attribute.
  
        Returns
        -------
        res : anything
            Results
            
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
                self._save(res)
            else:
                self._result = res
            
            self.done = True
        else:
            res = self.load()

        return res
        
        
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
        
        id_dict = {key:self._serialize(val) for key,val in parameters.items() if not self._serialize(val) == '__unhashable__'}
        
        self.id = hashlib.sha1(str([ id_dict[key] for key in id_dict.keys() ])).hexdigest()
        return self.id
    
    
    def load(self):
        """
        Checks if the run results are already computed and return them if so.
        
        When the result is available in memory, it is
        returned. When it is available on disk, it is loaded and returned.
        When the result is not computed yet this returns :code:`None`
        
        Returns
        -------
        res : anything, :code:`None`
            Results, returns :code:`None` if the results are not available

        Examples
        --------
        >>> run.load()
        {'val': 10}
        
        """
        
        if self._saveresult:
            data = self._load()
            res = data['res']
            
            # if statement for compatibility with older saved runs
            if 'runtime' in data:
                self.runtime = data['runtime']
            
            if not 'parameters' in data:
                print('The loaded data is in the old style, to add functionality run \'batchpy.convert_run_to_newstyle(run)\'')
                
            
            return res
            
                
        else:
            return self._result
            
            
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
            os.remove(self.filename)
            self.done = False
            return True
        except:
            return False  
         
         
    @property
    def parameters(self):
        """
        Alias to self.load()
        
        """

        return self._parameters

        
    @property
    def result(self):
        """
        Alias to self.load()
        
        """

        return self.load()

        
    @property
    def index(self):
        """
        Returns the run index in its batch
        
        """
        return self.batch.run.index(self)
        
        
    @property
    def filename(self):
        """
        Returns the filename of the run
        
        """
        return os.path.join(self.batch.savepath , '{}_{}.npy'.format(self.batch.name,self.id))
        
        
    def _save(self,res):
        """
        Saves the result in res along with run identifiers
        
        Parameters
        ----------
        res : dict
            The result dictionary
        """
        
        parameters = {key:self._serialize(val) for key,val in self.parameters.items()}
        np.save(self.filename,{'res':res,'id':self.id,'runtime':self.runtime,'parameters': parameters})
        
        
    def _load(self):    
        """
        Loads all data from the file with the correct id if it exists, returns
        None otherwise
        
        """
        
        if os.path.isfile(self.filename):
            data = np.load(self.filename).item()
            return data
        else:
            raise Exception('Result not found, no file with filename: {}'.format(self.filename))

            
    def _serialize(self,val):
        """
        Serialize a parameter
        
        Parameters
        ----------
        val : anything
            a dictionary
            
        Notes
        -----
        Not all parameter types are serializable. If a parameter can not be
        serialized ``'__unserializable__'`` is returned
        
        """
        
        serialized = '__unhashable__'
          
        nametypes = [
            types.BuiltinFunctionType,
            types.BuiltinMethodType,
            types.ClassType,
            types.FunctionType,
            types.GeneratorType,
            types.InstanceType,
            types.LambdaType,
            types.MethodType,
            types.ModuleType,
            types.TypeType,
            types.UnboundMethodType
        ]
        
        
        if isinstance(val,types.CodeType):
            serialized = val.co_code
        elif isinstance(val,types.FileType):
            serialized = val.name
        else:
            for t in nametypes:
                if isinstance(val,t):
                    serialized = val.__name__
                    break
                    
            if serialized == '__unhashable__':
                string = str(val)
                if len(string)>0 and string[0]=='<' and string[-1]=='>' and 'at 0x' in string:
                    print('WARNING: parameter {} can not be hashed and is not included in the id which could lead to loss of data and undesired results'.format(val) )
                else:
                    serialized = val
        
        return serialized
 

    def _check_result(self):
        """
        Checks if a result file is stored on the disk
       
        Checks if a file with the correct name can be found. Is so, it sets the 
        :code:`done` attribute to True. If not, the :code:`done` attribute is
        set to false.
        
        Examples
        --------
        >>> run._check_result()
        >>> run.done
        False
        
        """
        
        # check if there are results saved with the same id
        if os.path.isfile(self.filename):
            self.done = True
        else:
            self.done = False
    

    
class ResultRun(Run):
    """
    A class to load run results
    
    """
    
    def __init__(self,batch,id):
        
        
        self.batch = batch
        self.runtime = None
        self.done = True
        self._parameters = None
        self._saveresult = True
        self._result = None
        
        self.id = id
        
        
        data = self._load() 
        if 'runtime' in data:
            self.runtime = data['runtime']
            
        if 'parameters' in data:
            self._parameters = data['parameters']
            
        del data
    
    
    def run(self,**kwargs): 
        pass
        
    def __call__(self):
        self.done = True
        super(ResultRun,self).__call__()
        
    def _save(self):
        pass
           
    def clear(self):
        pass
        
        
def convert_run_to_newstyle(run):
    """
    Converts a saved run result to include the parameters
    
    Parameters
    ----------
    run : batchpy.Run object or child class
        The run to convert the result from
    """
    
    res = run.load()
    if not res is None:
        run._save(res)
        
        