#!/usr/bin/env python
import unittest
import batchpy
import python_git_package as pgp


class TestDoc(unittest.TestCase):
    
    def test_quickstart_example(self):
        success = pgp.rstpy('../doc/source/quickstart.rst',output=False)
        self.assertEqual(success,True)

        
        
if __name__ == '__main__':
    unittest.main()