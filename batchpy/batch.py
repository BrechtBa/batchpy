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
from multiprocessing import Pool

from .run import ResultRun


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

    def __init__(self, name, path='', saveresult=True, processes=1):
        """
        Creates a batch.

        Parameters
        ----------
        name : string
            A name for the batch

        path : string, optional
            A optional path to store results, if not provided the current path is
            chosen.

        saveresult : boolean, optional
            Save the results to disk or not, this argument is passed to all runs.

        processes : int, optional
            Number of multiprocessing processes to run the batch.

        Examples
        --------
        >>> batch = batchpy.Batch('mybatch')

        """
        self.name = name
        self.path = path
        self.processes = processes

        self.run = []
        self._saveresult = saveresult

    def add_run(self, runclass, parameters):
        """
        Adds a run

        Parameters
        ----------
        runclass : :py:meth:`~batchpy.run.Run` subclass
            A class reference which creates an object when supplied the
            parameters.

        parameters : dict
            A dictionary of parameters to be supplied to the
            :py:meth:`~batchpy.run.Run.run` method of the runclass.

        Examples
        --------
        >>> batch.add_run(Myrun,{'A':1,'B':[1,2,3],'C':'spam'})
        >>> batch()

        """

        run = runclass(self, saveresult=self._saveresult, **parameters)
        self.run.append(run)

    def add_factorial_runs(self, runclass, parameters):
        """
        Adds a full factorial design of runs based on parameter lists

        Parameters
        ----------
        runclass : :py:meth:`batchpy.run.Run` subclass
            A class reference which creates an object when supplied the
            parameters.

        parameters : dict
            A dictionary of lists of parameters to be supplied to the
            :py:meth:`~batchpy.run.Run.run` method of the runclass.

        Examples
        --------
        >>> batch.add_factorial_runs(Myrun,{'par1':[0,1,2],'par2':[5.0,7.1]})
        >>> # is equivalent with:
        >>> batch.add_run(Myrun,{par1:0,par2:5.0})
        >>> batch.add_run(Myrun,{par1:0,par2:7.1})
        >>> batch.add_run(Myrun,{par1:1,par2:5.0})
        >>> batch.add_run(Myrun,{par1:1,par2:7.1})
        >>> batch.add_run(Myrun,{par1:2,par2:5.0})
        >>> batch.add_run(Myrun,{par1:2,par2:7.1})

        """

        # replace strings with a list with a single element
        for k, v in parameters.items():
            if type(v) == str:
                parameters[k] = [v]
            elif not hasattr(v, '__len__'):
                parameters[k] = [v]

        valslist = list(itertools.product(*parameters.values()))

        for vals in valslist:
            par = {key: val for key, val in zip(parameters.keys(), vals)}
            self.add_run(runclass, par)

    def add_resultrun(self, id):
        """
        Adds saved runs by id

        Parameters
        ----------
        id : string or list of strings
            The id of the run.

        Examples
        --------
        >>> batch.add_resultrun('3ecc784a9d5cf26eb6420de2a43f04b310073925')

        """

        if not hasattr(id, '__iter__'):
            id = [id]

        for idi in id:
            r = ResultRun(self, idi)
            self.run.append(r)

    def get_runs_with(self, **kwargs):
        """
        Returns a list of runs with the specified parameter values

        Parameters
        ----------
        kwargs : anything
            Keyword arguments of parameter values .
            Several conditions can be appended to a parameter:
            `__eq`: equal, same as appending nothing
            `__ne`: not equal
            `__ge`: greater or equal
            `__le`: less or equal

        Returns
        -------
        runs : list
            a list of runs

        Examples
        --------
        >>> batch = batchpy.Batch('mybatch')
        >>> batch.add_factorial_runs(Myrun,{'par1':[0,1,2],'par2':[5.0,7.1]})
        >>> runs = batch.get_runs_with(par1=0)
        >>> print(runs)
        >>> runs = batch.get_runs_with(par1__ge=1,par2=5.0)
        >>> print(runs)

        """

        runs = []
        for run in self.run:
            add = True
            for key, val in kwargs.items():

                if key.endswith('__eq'):
                    def condition(par, val):
                        try:
                            return np.isclose(par, val)
                        except:
                            return par == val
                    key = key[:-4]

                elif key.endswith('__ne'):
                    def condition(par, val):
                        try:
                            return not np.isclose(par, val)
                        except:
                            return not par == val
                    key = key[:-4]

                elif key.endswith('__ge'):
                    def condition(par, val):
                        return par >= val
                    key = key[:-4]

                elif key.endswith('__le'):
                    def condition(par, val):
                        return par <= val
                    key = key[:-4]

                else:
                    def condition(par, val):
                        try:
                            return np.isclose(par, val)
                        except:
                            return par == val

                # check the condition
                if key in run.parameters:
                    con = condition(run.parameters[key], val)
                    if hasattr(con, '__iter__'):
                        con = con.all()

                    if not con:
                        add = False
                        break

            if add:
                runs.append(run)

        return runs

    def __call__(self, runs=-1, verbose=1):
        """
        Runs the remainder of the batch or a specified run

        Parameters
        ----------
        runs : int or list of ints, optional
            Indices of the runs to be executed, -1 for all runs

        verbose : int, optional
            Integer determining the amount of printed output 0/1/2

        """

        # check which runs are to be done
        expandedruns = []

        if isinstance(runs, list) or isinstance(runs, np.ndarray):
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

        def success_callback(result):
            i = result['i']
            run_inds = result['run_inds']
            self.run[run_inds[i]]._done = True
            self.run[run_inds[i]]._runtime = result['runtime']
            if self.run[run_inds[i]]._saveresult:
                self.run[run_inds[i]]._save(result['res'])
            else:
                self.run[run_inds[i]]._result = result['res']
            if verbose > 0:
                print_progress(i, run_inds, starttime, self.run, async=True, verbose=verbose)

        if self.processes > 1:
            starttime = time.time()
            with Pool(processes=self.processes) as pool:
                for i in range(len(expandedruns)):
                    pool.apply_async(run_async, args=(i, expandedruns, starttime, self.run,), callback=success_callback)

                pool.close()
                pool.join()
        else:
            starttime = time.time()
            for i in range(len(expandedruns)):
                if verbose > 0:
                    print_progress(i, expandedruns, starttime, self.run, async=False, verbose=verbose)
                self.run[expandedruns[i]]()

        runtime = time.time() - starttime

        if verbose > 0:
            print('total runtime {0:.1f} min'.format(runtime / 60))
            print('done')
            sys.stdout.flush()

    def save_ids(self, filename=None, format='npy'):
        """
        Saves all ids in the batch to a python file with an ``ids`` list

        Parameters
        ----------
        filename : str, optional
            The filename of the output file. If no filename is supplied a
            file is created in the ``_res`` folder, named ``batchname_ids.npy``
            or ``batchname_ids.py`` depending on the format argument.
            If a filename is supplied, the format argument is ignored and the
            filename extension is used to determine the format.

        format : str, optional
            The format to save the ids to, 'npy'/'py'. By default, a .npy file
            is created, the ids can be retrieved with
            ``ids = np.load('batchname_ids.npy')``. If the 'py' format is
            supplied the ids are written to a python file in a list.

        Examples
        --------
        >>> batch.save_ids()

        In another interpreter:

        >>> import numpy as np
        >>> ids = np.load('_res/mybatch_ids.npy')
        >>> print(ids)

        """

        if filename is None:
            filename = os.path.join(self.savepath, '{}_ids.{}'.format(self.name, format))
        else:
            format = os.path.splitext(filename)[1][1:]

        if format == 'npy':
            np.save(filename, [run.id for run in self.run])

        elif format == 'py':
            with open(filename, 'w') as f:

                f.write('ids = [\n')
                for run in self.run:
                    f.write('    \'{}\',\n'.format(run.id))

                f.write(']')
        else:
            raise Exception('Format \'{}\' not recognized, should be \'npy\' or \'py\'.'.format(format))

    @property
    def savepath(self):
        """
        Property returning the path where files are saved

        """
        dirname = os.path.join(self.path, '_res')

        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        if not os.path.exists(os.path.join(dirname, '__init__.py')):
            with open(os.path.join(dirname, '__init__.py'), 'w'):
                pass

        return dirname

    def _get_filenames(self):
        """
        Returns a list of found files which correspond to the batch
        """

        dirname = self.savepath
        filenames = []
        files = [f for f in os.listdir(dirname) if re.match(self.name + r'_run.*\.npy', f)]
        for f in files:
            filenames.append(os.path.join(dirname, f))

        return filenames


# helper functions
def strlist(runs):
    """
    Returns a pretty formatted string list with dots if there are too many
    elements.
    """
    if len(runs) > 5:
        return '[' + str(runs[0]) + ',' + str(runs[1]) + ',...,' + str(runs[-2]) + ',' + str(runs[-1]) + ']'
    else:
        return str(runs)


def print_progress(i, run_inds, starttime, runs, async=False, width=80, verbose=2):
    """
    Prints the progress of a set of runs
    """
    if async:
        skipindex = len([1 for i in run_inds if runs[i].done])
    else:
        skipindex = i

    if verbose > 1:
        skip = 1
    elif verbose > 0:
        skip = int(np.ceil(len(run_inds) / 50.))
    else:
        skip = 1

    if skipindex % skip == 0:
        runtime = time.time() - starttime
        if runtime > 3600:
            runtime_str = '{0:.1f} h'.format(runtime / 3600)
        else:
            runtime_str = '{0:.1f} min'.format(runtime / 60)

        if i == 0:
            eta_str = '/'
        else:
            if async:
                n_done = len([1 for i in run_inds if runs[i].done])
                n_total = len(run_inds)
            else:
                n_done = i
                n_total = len(run_inds)
            eta = runtime / n_done * (n_total - n_done)
            if runtime > 60:
                eta_str = '{0:.1f} h'.format(eta / 3600)
            else:
                eta_str = '{0:.1f} min'.format(eta / 60)

        progress_str = '### '
        if async:
            progress_str += 'finished '
        progress_str += 'run {0} in '.format(run_inds[i])

        progress_str += strlist(run_inds)
        progress_str += (40 - len(progress_str)) * ' '
        progress_str += 'runtime: {}'.format(runtime_str)
        progress_str += 4 * ' '
        progress_str += 'eta: {}'.format(eta_str)
        progress_str += (width - len(progress_str) - 3) * ' ' + '###'

        print(progress_str)
        sys.stdout.flush()


def run_async(i, run_inds, starttime, runs):
    res, runtime = runs[run_inds[i]]._run()
    return {'res': res, 'runtime': runtime, 'run_inds': run_inds, 'i': i, 'starttime': starttime}


def clear_res():
    folder = '_res'
    try:
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
    except Exception as e:
        print(e)
