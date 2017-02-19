import batchpy

################################################################################
# Define a Run class, sub-classing batchpy.Run
################################################################################
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
        
        
################################################################################
# Define a batch
################################################################################
# The batch name will be used to identify result files belonging to the batch
batch = batchpy.Batch('example')



################################################################################
# Add runs 
################################################################################
# Add single run
batch.add_run( example_run,{'A':10,'B':[3,2,4,3,8]})

# Add a full factorial design of runs
batch.add_factorial_runs( example_run,
                         {'A': [1,2,3,4,5],
                          'B': [[2,5,8],[1,9,6,3,9],[6,4,0,9,4,1]],
                          'operator': [min,max,sum,len]})
                          
print([run.done for run in batch.run])



################################################################################
# Run all computations
################################################################################
batch()



################################################################################
# Add another run and run again
################################################################################
batch.add_run( example_run,{'A':8,'operator':min})

# only the last run will computed as the other results are already available
batch()



################################################################################
# Retrieve results
################################################################################
res = batch.run[0].load()
print(res)



################################################################################
# Create a result batch
################################################################################
# with the ids of runs a batch with resultruns can be created even if the original run class is unavailable
ids = [run.id for run in batch.run]

del example_run
del batch

resultbatch = batchpy.Batch('example')
resultbatch.add_resultrun( ids )

res = resultbatch.run[0].load()
print(res)