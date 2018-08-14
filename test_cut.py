import unittest
from tools.cut import *
from math import *
from os import getcwd, listdir, sep, remove, error, path


class Test_cut(unittest.TestCase):
    def setUp(self):
        self.frame = Path(MicroLine(Coordinate(0, 0), Coordinate(20000, 0)),
                       MicroLine(Coordinate(20000, 0), Coordinate(20000, 20000)),
                       MicroLine(Coordinate(20000, 20000), Coordinate(0, 20000)),
                       MicroLine(Coordinate(0, 20000), Coordinate(0, 0)))
        
        self.p1 = Path(MicroLine(Coordinate(0, 0), Coordinate(10000, 0)),
          MicroLine(Coordinate(10000, 0), Coordinate(10000, 10000)),
          MicroLine(Coordinate(10000, 10000), Coordinate(0, 10000)),
          MicroLine(Coordinate(0, 10000), Coordinate(0, 0)))
        self.p1ps = [(1,1),(1,2),(2,1),(2,2)]



        self.p2 = Path(MicroLine(Coordinate(0, 0), Coordinate(10000, 0)),
                       MicroLine(Coordinate(10000, 0), Coordinate(10000, 15000)),
                       MicroLine(Coordinate(10000, 15000), Coordinate(5000, 15000)),
                       MicroLine(Coordinate(5000, 15000), Coordinate(5000, 10000)),
                       MicroLine(Coordinate(5000, 10000), Coordinate(0, 10000)),
                       MicroLine(Coordinate(0, 10000), Coordinate(0, 0)))
        self.p2ps = [(1, 1), (1, 2), (2, 1), (2, 2), (2, 3)]

        self.p3 = Path(MicroLine(Coordinate(0, 0), Coordinate(11000, 0)),
                       MicroLine(Coordinate(11000, 0), Coordinate(11000, 14900)),
                       MicroLine(Coordinate(11000, 14900), Coordinate(4900, 14900)),
                       MicroLine(Coordinate(4900, 14900), Coordinate(4900, 11000)),
                       MicroLine(Coordinate(4900, 11000), Coordinate(0, 11000)),
                       MicroLine(Coordinate(0, 11000), Coordinate(0, 0)))
        self.p3ps = [(1, 1), (1, 2), (2, 1), (2, 2), (2, 3)]

        self.p4 = Path(MicroLine(Coordinate(0, 0), Coordinate(1, 0)),
                       MicroLine(Coordinate(1, 0), Coordinate(1, 1)),
                       MicroLine(Coordinate(1, 1), Coordinate(0, 1)),
                       MicroLine(Coordinate(0, 1), Coordinate(0, 0)))

        self.p5 = Path(MicroLine(Coordinate(2, 2), Coordinate(3, 2)),
                       MicroLine(Coordinate(3, 2), Coordinate(3, 3)),
                       MicroLine(Coordinate(3, 3), Coordinate(2, 3)),
                       MicroLine(Coordinate(2, 3), Coordinate(2, 2)))

        self.p6 = Path(MicroLine(Coordinate(2, 0), Coordinate(3, 0)),
                       MicroLine(Coordinate(3, 0), Coordinate(3, 3)),
                       MicroLine(Coordinate(3, 3), Coordinate(2, 3)),
                       MicroLine(Coordinate(2, 3), Coordinate(2, 0)))
    '''
    def test_unitdivision(self):
        edge = unitdivision(self.p1)
        self.assertEqual(edge, round(sqrt(11000), 2))

    def test_subunit(self):
        self.assertEqual(set(subunit(self.p1, 5000, self.frame)), set(self.p1ps))
        self.assertEqual(set(subunit(self.p2, 5000, self.frame)), set(self.p2ps))
        self.assertEqual(set(subunit(self.p3, 5000, self.frame)), set(self.p3ps))
        
    '''
    def test_two_paths_distance(self):
        self.assertEqual(two_paths_distance(self.p4, self.p5), sqrt(2))
        self.assertEqual(two_paths_distance(self.p4, self.p6), 1)