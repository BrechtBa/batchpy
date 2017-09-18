#!/usr/bin/env python
import unittest
import os
import subprocess

class TestDoc(unittest.TestCase):
    
    def test_quickstart_example(self):
        fnull = open(os.devnull, 'w')
        res = subprocess.call(['python', 'doc/source/examples/quickstart.py'],stdout=fnull)
        self.assertEqual(res,0)
        
        
if __name__ == '__main__':
    unittest.main()
