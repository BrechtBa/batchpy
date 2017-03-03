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


import batchpy

# define a run class
class example_run(batchpy.Run):
    """
    An example run class
    """
    def run(self,A=0,B=[1,2,3],operator=max):
        """
        An example computation function
        
        """
        
        print(self.parameters)

        res = {'val': self.parameters['A']*self.parameters['operator'](self.parameters['B'])}
        
        return res
        
# define a batch
batch = batchpy.Batch('example')


# Add single run
batch.add_run( example_run,{'A':10,'B':[3,2,4,3,8]})

# Add a full factorial design of runs
batch.add_factorial_runs( example_run,
                         {'A': [1,2,3,4,5],
                          'B': [[2,5,8],[1,9,6,3,9],[6,4,0,9,4,1]],
                          'operator': [min,max,sum,len]})
                          
# run properties
print( batch.run[0].parameters )
print( batch.run[0].id )
print( batch.run[0].index )
print( batch.run[0].done )
print( batch.run[0].result )
print( batch.run[0].runtime )

# run filename
print( batch.run[0].filename )

# get runs with
runs = batch.get_runs_with(A__ge=3,B=[2,5,8],operator=max)
print(runs)

#run the batch
batch()

# retrieve results
res = batch.run[0].result
print(res)

runs = batch.get_runs_with(A__le=3,B=[2,5,8],operator=min)
res = [run.result['val'] for run in runs]
print(res)

# add new run
batch.add_run( example_run,{'A':8,'operator':min})
print([run.done for run in batch.run])
batch()
    
    
# use of the resultrun class    
# create a resultbatch    
ids = [run.id for run in batch.run]

del example_run
del batch

resultbatch = batchpy.Batch('example')
resultbatch.add_resultrun( ids )

# retrieve results from the resultbatch
res = resultbatch.run[0].result
print(res)


# create result batch from id file    
resultbatch.save_ids()
del resultbatch
    
import numpy as np
ids = np.load('_res/example_ids.npy')
print(ids)

resultbatch = batchpy.Batch('example')
resultbatch.add_resultrun( ids )

res = resultbatch.run[0].result
print(res)
