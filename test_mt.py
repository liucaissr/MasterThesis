import unittest
from tools.mt import *
from os import getcwd, listdir, sep, remove, error, path



class Test_cut(unittest.TestCase):
    def test_num_digit(self):
        self.assertEqual(num_digit(0.05), 2)
        self.assertEqual(num_digit(0.5), 1)
        self.assertEqual(num_digit(15), 0)
        self.assertEqual(num_digit(0.0015), 3)


