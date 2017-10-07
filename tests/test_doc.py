#!/usr/bin/env python
import unittest
import os
import sys

f = open(os.devnull, 'w')
sys.stdout = f


class TestDoc(unittest.TestCase):
    def test_quickstart_example(self):
        from doc.source.examples import quickstart
        self.assertEqual(quickstart.res, {'val': 80})


if __name__ == '__main__':
    unittest.main()
