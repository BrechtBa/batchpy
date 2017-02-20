batchpy
=======

A package to run large or small batches of similar calculations and storing the results so no double calculations are performed.

The example below should explain the work flow

Installation
------------
requires:

- ``numpy``


To install run::

    pip install batchpy


Example
-------

First import batchpy::

    import batchpy


Create a run class, subclassing the batchpy.Run class to create objects with a run method which when called performs the required calculations and return a result dictionary.
All parameters should be passed as named parameters to add default and to make their names available:

.. code::

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
            

Now define a batch using ``batchpy.Batch`` and supply a name to the batch. The name will be used to identify results files.

.. code::

    batch = batchpy.Batch('my_batch')

Result files are saved and retrieved from a subdirectory "_res" of the base path.
If this directory doesn't exist it will be created.

Next we can add runs to our batch. This can be done run per run:

.. code::

    batch.add_run( example_run,{'A':10,'B':[3,2,4,3,8]})

        
Or from a full factorial design:

.. code::

    batch.add_factorial_runs( example_run,
                         {'A': [1,2,3,4,5],
                          'B': [[2,5,8],[1,9,6,3,9],[6,4,0,9,4,1]],
                          'operator': [min,max,sum,len]})
                          

All calculations can be executed by calling the batch:

.. code::

    batch()


Results can be retrieved by loading them. This is required as they are not kept in memory to allow large batches to be run:

.. code::

    res = batch.run[0].load()


Results are stored in the _res folder in a ``.npy`` format.

When a file containing a batch definition is rerun, the calculation that have already run (with id's present in the saved file) will not be rerun.
This makes the class useful for runs with long computation times.
We can for instance extend the batch with an additional run:

.. code::

    batch.add_run( example_run,{'A':8,'operator':min})


Using the attribute ``done``, we can check which runs are done and which need to be executed:

.. code::

    print([run.done for run in batch.run])


Calling the the batch again will execute only those runs which have not been run yet:

.. code::

    batch()


Try closing and restarting python and rerun the above code. You will notice no new calculations are performed, all results are loaded from the previously saved file.
You can also try changing one parameter in a run definition, now only the changed runs will be rerun.


 
