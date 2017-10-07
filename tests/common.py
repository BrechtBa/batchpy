#!/usr/bin/env python
import batchpy
import os
import numpy as np


class MyRun(batchpy.Run):
    def run(self, A=1000, B=None, C=np.mean):
        if B is None:
            B = []
        a = []
        for i in range(A):
            a.append(i)
        return {'a': a, 'b': B, 'c': C(a)}


def clear_res():
    folder = '_res'
    try:
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
    except Exception as e:
        print(e)
