#!/usr/bin/env python
import batchpy
import os
import numpy as np


# the run class used for testing
class testclass(batchpy.Run):
    def run(self,A=1000,B=[],C=np.mean):
        """
        Do something which takes some time and requires some memory
        
        """
        
        a = []
        for i in range(A):
            a.append(i)
        
        return {'a':a,'b':B,'c':C(a)}


        
# clear result folder
def clear_res():
    folder = '_res'
    try:
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)

            if os.path.isfile(file_path):
                os.unlink(file_path)
           
    except Exception as e:
        print(e)
        
