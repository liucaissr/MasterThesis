import unittest
from os import getcwd, listdir, sep, remove, error, path


class Test_cut(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        outputpath = '/Users/my/Desktop/MasterThesis/source/output/'
        resultpath = outputpath + max(listdir(outputpath)) + sep
        realpath = '/Users/my/Desktop/MasterThesis/mt1git/zxj/'

    def test_svg(self):
        pass

    def test_conflict(self):

