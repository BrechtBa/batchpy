Quickstart
==========

.. toctree::
    :maxdepth: 3
    
    
Batchpy is intended as a framework for managing and running large batches of similar calculations.
Calculations are defined in :py:meth:`~batchpy.run.Run` objects which are used to run calculations and store and retrieve results.
The user is responsible for defining a run class, sub classing the built-in :py:meth:`batchpy.run.Run` class.
The main requirement is the definition of a :py:meth:`~batchpy.run.Run.run` method, which runs the computations and returns a result.
The :py:meth:`~batchpy.run.Run.run` method must accept a series of keyword arguments which can be used during the calculations.
If required, custom methods can be added to enable creating several types of runs in an object oriented way.
A very simple example:

.. literalinclude:: examples/quickstart.py
   :lines: 21-38

   
Managing which runs are executed and which need to be run is done by a :py:meth:`batchpy.batch.Batch` object.
The batch name defines the filenames which are given to run results.

.. literalinclude:: examples/quickstart.py
   :lines: 41


Creating a run instance requires a reference to a :py:meth:`~batchpy.batch.Batch` object and the parameters to add to the run and should be done through the :py:meth:`~batchpy.batch.Batch` methods.
Runs can be added to a batch one by one using the :py:meth:`~batchpy.batch.Batch.add_run` method, requiring a run class and a dictionary of run parameters as arguments.
A method to add a full factorial design of runs (:py:meth:`~batchpy.batch.Batch.add_factorial_run`) is also provided which requires a run class and a dictionary of lists of parameters as arguments.
The runs are stored in a list and are accessible through the :py:meth:`~batchpy.batch.Batch.run` attribute.

.. literalinclude:: examples/quickstart.py
   :lines: 44-51


A run has :py:attr:`~batchpy.run.Run.parameters`, :py:attr:`~batchpy.run.Run.id`, :py:attr:`~batchpy.run.Run.index`, :py:attr:`~batchpy.run.Run.done`, :py:attr:`~batchpy.run.Run.result` and :py:attr:`~batchpy.run.Run.runtime` properties to access the run details.
 
.. literalinclude:: examples/quickstart.py
   :lines: 54-59

    
By default the run results are saved to disk in a ``_res`` folder which is created if it is not present.
Each run is given an id based on the parameters supplied to the run.
The default id is a 40 character hash, however, the id creation can be customized by changing the run :py:meth:`~batchpy.run.Run.generate_id` method which takes a parameter dictionary as arguments. 
Run result files are named ``"batch.name"_"run.id".npy`` and stored in the ``_res`` folder.

.. literalinclude:: examples/quickstart.py
   :lines: 62
    
    
When two runs with the same parameters are created, they have the same id and the computation will not be repeated but the second run will use the results of the 1st run as its own.
The user can choose not to save the run results, for instance for testing, by specifying ``saveresult=False`` upon creating the batch.


For easy retrieving runs with certain parameters the :py:meth:`~batchpy.batch.Batch.get_runs_with` method is provided.
It can be supplied with keyword argument pairs to retrieve a list of runs with matching parameters.
The parameter names can be appended with ``__ne``, ``__ge`` and ``__le`` to retrieve values where the parameter is not equal, greater or equal and less or equal respectively.

.. literalinclude:: examples/quickstart.py
   :lines: 65-66

    
Running all calculations is done by calling the batch object.

.. literalinclude:: examples/quickstart.py
   :lines: 69

    
Results for a run can be retrieved through the :py:attr:`~batchpy.run.Run.result` attribute.
Together with the :py:meth:`~batchpy.batch.Batch.get_runs_with` method this is very flexible.


.. literalinclude:: examples/quickstart.py
   :lines: 72-77
   
    
At any time runs can be added to the batch.
When the batch is called again, only runs for which no results are available are recomputed, other results will be retrieved from the disk.

.. literalinclude:: examples/quickstart.py
   :lines: 80-82


The workflow ``Batchpy`` was designed for is to define and call a batch as don in the example above, in a separate python script.
In other scripts, for instance for plotting some of the results, this batch can then be imported and results can be easily retrieved.


ResultRun
---------

Sometimes it is required to use results of some calculation without importing the entire computation method and all required functions and classes.
For example, to pass results to a colleague, without them having to install a ton of packages.
For this use case, a :py:meth:`batchpy.run.ResultRun` class was developed.

A :py:meth:`~batchpy.run.ResultRun` is a subclass of the :py:meth:`~batchpy.run.Run` class.
Results of runs can be added to a batch with the :py:meth:`~batchpy.batch.Batch.add_resultrun` method and the run id or a list of run ids.
The actual run class which computed the results is not required and does not need to be defined.

.. literalinclude:: examples/quickstart.py
   :lines: 87-93


Results can be retrieved from a :py:meth:`~batchpy.run.ResultRun` in exactly the same way as an ordinary run, making them interesting for passing data around or creating plotting scripts.

.. literalinclude:: examples/quickstart.py
   :lines: 96-97


Run ids can be written to a script and imported in other scripts to create a batch of result runs.
The :py:meth:`~batchpy.batch.Batch` object provides a :py:meth:`~batchpy.batch.Batch.save_ids` method to write all ids of the batch to a python file which can be imported from the ``_res`` folder.

.. literalinclude:: examples/quickstart.py
   :lines: 101-112

