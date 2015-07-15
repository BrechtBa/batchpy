# batchpy
A package to run large or small batches of similar calculations and storing the results so no double calculations are performed.

The example below should explain the workflow

### Dependencies
requires `numpy`


## Example

Firstly import batchpy
```
import batchpy
```

Define a run class to create objects which when called run the required calculations and return a result dictionary.
It is best to assign a unique string id attribute in each run. This id can be created using a hash of a selection of parameters as strings using "hashlib":
```
import hashlib

class Run:
	def __init__(self,parameter_A,parameter_B=None,parameter_C=[1,2,3],parameter_D={'A':1,'B':None},parameter_E='test'):
		"""
		creates a run instance with all parameters required for the calculations
		assigns an id attribute derived from the parameters so when a parameter changes the run id changes.
		
		Parameters:
		all parameters you need
		"""
		
		self.id = hashlib.sha1(str([parameter_A,parameter_C,parameter_D,parameter_E])).hexdigest()
		
		self.parameter_A = parameter_A
		self.parameter_B = parameter_B
		self.parameter_C = parameter_C
		self.parameter_D = parameter_D
		self.parameter_E = parameter_E
	
	def __call__(self):
		"""
		perform calculations and set the results in res
		
		Parameters: 
		no parameters allowed
		
		Returns:
		a results dictionary
		"""
		
		# do some complex computations and set the results you want to save in res
		result_1 = 10
		res = {'result_1': result_1}
		
		return res
```

Now define a batch using `batchpy.Batch`.
```
batch = batchpy.Batch('my_batch')
```
This function has a required argument, the batch name, which will be the name of the saved result file.
There is also an optional argument, path, which determines the base path. If path is not supplied the current directory will be the base path.
Result files are saved and retrieved from a subdirectory "_res" of the base path. If this directory doesn't exist it will be created.

Next we can add runs to our batch. This can be done run per run or in a loop:
```
for i in range(5):
	batch.add_run(Run('temp_parameter_A',parameter_B=i,parameter_C=[4,5,6]))
```

Or from a full factorial design:
```
batch.add_factorial_run(Run,{'parameter_A':'temp_parameter_A',
							 'parameter_C':[[4,5,6],[7,8,9]],
							 'parameter_E': ['E1','E2','E3']})
```
The latter code will create runs with all possible combinations of parameter_C and parameter_E, 6 runs in this case.

All calculations can be executed by calling the batch:
```
batch()
```

Results and runs can easily be accessed using the batch attributes `run` and `res` which are lists of all run objects and all res dictionaries respectively:
```
print(batch.run[4].parameter_B)
print(batch.res[4]['result_1'])
```

Results are stored in the _res folder in a `.npz` format.

When a file containing a batch definition is rerun, the calculation that have allready run (with id's present in the saved file) will not be rerun.
This makes the class useful for runs with long computation times.
We can for instance extend the batch with additional runs:
```
for i in range(5):
	batch.add_run(Run('temp_parameter_A',parameter_B=i+20,parameter_C=[1,2,3]))
```

Using the attribute `rundone`, we can check which runs are done and which need to be executed:
```
print(batch.rundone)
```

Calling the the batch again will execute only those runs which have not been run yet:
```
batch()
```

Try closing and restarting python and rerun the above code. You will notice no new calculations are performed, all results are loaded from the previously saved file.
You can also try changing one parameter in a run definition, now only the changed runs will be rerun.


 
