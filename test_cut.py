import unittest
from tools.cut import *
from os import getcwd, listdir, sep, remove, error, path


class Test_cut(unittest.TestCase):
    def setUp(self):
        self.p1 = Path(MicroLine(Coordinate(0, 0), Coordinate(10000, 0)),
          MicroLine(Coordinate(10000, 0), Coordinate(10000, 10000)),
          MicroLine(Coordinate(10000, 10000), Coordinate(0, 10000)),
          MicroLine(Coordinate(0, 10000), Coordinate(0, 0)))

    def test_unitdivision(self):
        edge = unitdivision(self.p1)
        AssertionError(edge, round(math.sqrt(1.1), 2))





