import unittest
from tools.segment import *
from math import *
from os import getcwd, listdir, sep, remove, error, path

class Test_nomerge(unittest.TestCase):
    def setUp(self):
        self.p1 = Pattern(MicroLine(Coordinate(0, 0), Coordinate(10, 0)),
                          MicroLine(Coordinate(10, 0), Coordinate(10, 10)),
                          MicroLine(Coordinate(10, 10), Coordinate(0, 10)),
                          MicroLine(Coordinate(0, 10), Coordinate(0, 0)))

        self.p2 = Pattern(MicroLine(Coordinate(5, 2), Coordinate(20, 2)),
                          MicroLine(Coordinate(20, 2), Coordinate(20, 8)),
                          MicroLine(Coordinate(20, 8), Coordinate(5, 8)),
                          MicroLine(Coordinate(5, 8), Coordinate(5, 2)))

        self.p3 = Pattern(MicroLine(Coordinate(0, 0), Coordinate(4, 0)),
                          MicroLine(Coordinate(4, 0), Coordinate(4, 10)),
                          MicroLine(Coordinate(4, 10), Coordinate(0, 10)),
                          MicroLine(Coordinate(0, 10), Coordinate(0, 0)))


    def test_nomerge(self):
        self.assertEqual(two_paths_distance(self.p1, self.p2), 0)
        self.assertEqual(two_paths_distance(self.p3, self.p2), 1)