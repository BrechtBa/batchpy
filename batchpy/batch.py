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
import sys
import re
import numpy as np
import itertools
import time

class Batch(object):
    """
    The batchpy batch class
    
    A batch can contain several runs of computations. Using batchpy these
    batches can be easily defined using python files (to support version
    control) and run.
    
    The computation results can be stored in memory or saved to disk per run.
    When the result of a run is saved it is cleared from memory which allows for
    computations which would require more memory then available if all runs were
    to be executed at once.
    
    """
    
    def __init__(self,name,path='',saveresult=True):
        """
        creates a batch
        
        Parameters
        ----------
        name : string
            a name for the batch
            
        path : string
            a optional path to store results, if not provided the current
            path is chosen
            
        saveresult : boolean
            save the results to disk or not, this argument is passed to all
            runs
                
        Examples
        --------
        >>> batch = batchpy.Batch('mybatch',path='res')
        
        """
        
        self.name = name
        self.path = path
        
        self.run = []
        self._saveresult = saveresult
        
    def add_run(self,runclass,parameters):
        """
        Adds a run
        
        Parameters
        ----------
        runclass : class
            a class reference which creates an object when supplied the
            parameters
            
        parameters : dict
            a dictionary of parameters to be supplied to the init function of
            the runclass
        
        Examples
        --------
        >>> batch.add_run(Cal,{'A':1,'B':[1,2,3],'C':'spam'})
        >>> batch()
        
        # will run cal() and store the return of cal() in batch.res[] after completion
        # the run will be assigned an id according to cal.id
        
        """
        
        run = runclass(self,saveresult=self._saveresult,**parameters)
        self.run.append(run)
        
        # set the run index
        run.index = self.run.index(run)
        
        
    def add_factorial_runs(self,runclass,parameters):
        """
        Adds runs 
        
        Parameters
        ----------
        runclass : class
            a class reference which creates an object when supplied the
            parameters
        
        parameters : dict
            a dictionary of lists of parameters to be supplied to the init
            function of the runclass
        
        Examples
        --------
        >>> batch.add_factorial_runs(Cal,{'par1':[0,1,2],'par2':[5.0,7.1]})
        
        # is equivalent with:
        >>> batch.add_run(Cal(par1=0,par2=5.0))
        >>> batch.add_run(Cal(par1=0,par2=7.1))
        >>> batch.add_run(Cal(par1=1,par2=5.0))
        >>> batch.add_run(Cal(par1=1,par2=7.1))
        >>> batch.add_run(Cal(par1=2,par2=5.0))
        >>> batch.add_run(Cal(par1=2,par2=7.1))
        
        """
        
        valslist = list(itertools.product(*parameters.values()))
        
        for vals in valslist:
            par = {key:val for key,val in zip(parameters.keys(),vals)}
            self.add_run( runclass,par )
            
    def add_run_by_id(self,id):
        """
        Adds saved runs by id
        
        Parameters
        ----------
        id : string or list of strings
        """
        
        if not hasattr(id,'__iter__'):
            id = [id]
        print(id)    
            
            
    def get_runs_with(self,**kwargs):
        """
        Returns a list of runs with the specified parameter values
        
        Parameters
        ----------
        key=value pairs of parameters
        
        Several conditions can be appended to a parameter:
        `__eq`: equal, same as appending nothing
        `__ne`: not equal
        `__ge`: greater or equal
        `__le`: less or equal
        
        Example
        -------
        
        """
        
        runs = []
        for run in self.run:
            add = True
            for key,val in kwargs.items():
            
                # create the condition
                if key.endswith('__eq'):
                    condition = lambda par,val: np.isclose( par,val )
                    key = key[:-4]
                if key.endswith('__ne'):
                    condition = lambda par,val: not np.isclose( par,val )
                    key = key[:-4]
                elif key.endswith('__ge'):
                    condition = lambda par,val: par >= val
                    key = key[:-4]
                elif key.endswith('__le'):
                    condition = lambda par,val: par <= val
                    key = key[:-4]
                else:
                    condition = lambda par,val: np.isclose( par,val )
                    
                # check the condition
                if key in run.parameters:
                    con = condition( run.parameters[key],val )
                    if hasattr(con,'__iter__'):
                        con = con.all()
                        
                    if not con:
                        add = False
                        break
  
            if add:
                runs.append(run)
                
        return runs
        
        
    def __call__(self,runs=-1):
        """
        Runs the remainder of the batch or a specified run
        
        Parameters
        ----------
        runs : int or list of ints
            indices of the runs to be executed, -1 for all runs
            
        """
        title_width = 80
        
        # check which runs are to be done
        expandedruns = []
        
        if isinstance(runs,list) or isinstance(runs,np.ndarray):
            for ind in runs:
                if not self.run[ind].done:
                    expandedruns.append(ind)
        else:        
            if runs < 0:
                for ind in range(len(self.run)):
                    if not self.run[ind].done:
                        expandedruns.append(ind)
                        
            elif not self.run[runs].done:
                expandedruns.append(runs)
    
        # derermine when to print the title string
        skip = int( np.ceil( len(expandedruns)/50. ) )
            
        starttime = time.time()
        for i,run in enumerate(expandedruns):
            
            # print the run title string
            if i%skip==0:
                runtime = time.time()-starttime
                if i==0:
                    etastr = '/'
                else:
                    etastr = '{0:.1f} min'.format( runtime/i*(len(expandedruns)-i)/60 )
                    
                title_str = '### run {0} in '.format(run)
                title_str += strlist(expandedruns)
                title_str += (40-len(title_str))*' '
                title_str += 'runtime: {0:.1f} min'.format(runtime/60)
                title_str += 4*' '
                title_str += 'eta: '+etastr
                title_str += (title_width-len(title_str)-3)*' ' +'###'
                print(title_str)
                
                # flush the printing cue
                sys.stdout.flush()

            # run the run
            self.run[run]()
        
        runtime = time.time()-starttime
        print('total runtime {0:.1f} min'.format(runtime/60))
        print('done')
        sys.stdout.flush()
        
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