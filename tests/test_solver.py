#!/usr/bin/env python3

import logging
import os
import sys
import unittest

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from nonogram.block import Block
from nonogram.column import Column
from nonogram.line import Line
from nonogram.raster import Raster
from nonogram.row import Row
from nonogram.solver import Solver

from nonogram.raster import BLACK
from nonogram.raster import UNKNOWN
from nonogram.raster import WHITE


class TestSolver(unittest.TestCase):

    def __init__(self, *args):
        logging.basicConfig(format='%(message)s', level=logging.DEBUG)
        # self.raster = Raster(table=[[]], row_meta=[], col_meta=[])

        super(TestSolver, self).__init__(*args)

    def test_solve(self):
        spec = """4 4
3
1 1
1 1
2
4
1 1
2
1""".split("\n")
        raster_internals = Raster.parse_metadata(spec)
        raster = Raster(**raster_internals)
        Solver().solve(raster)

    def test_fill_intersections(self):
        # if the line is solved (no UNKNOWN) then there's nothing to do...
        self.assertIsNone(Solver().fill_intersections(
            bytearray([BLACK, WHITE, BLACK]), Line(0, 0, [])))

        # block fills the whole line (row or column)
        mask = bytearray([UNKNOWN, UNKNOWN, UNKNOWN])
        Solver().fill_intersections(
            mask, Line(0, 3, [Block(start=0, end=2, length=3)]))
        self.assertEqual(bytearray([BLACK, BLACK, BLACK]), mask)

        # 3 overlapping cells
        mask = bytearray([UNKNOWN] * 5)
        Solver().fill_intersections(
            mask, Line(0, 5, [Block(start=0, end=4, length=4)]))
        self.assertEqual(
            bytearray([UNKNOWN, BLACK, BLACK, BLACK, UNKNOWN]), mask)

        # one overlapping cell
        mask = bytearray([UNKNOWN] * 5)
        Solver().fill_intersections(
            mask, Line(0, 5, [Block(start=0, end=4, length=3)]))
        self.assertEqual(
            bytearray([UNKNOWN, UNKNOWN, BLACK, UNKNOWN, UNKNOWN]), mask)

        # no overlapping cell
        mask = bytearray([UNKNOWN] * 5)
        Solver().fill_intersections(
            mask, Line(0, 5, [Block(start=0, end=4, length=2)]))
        self.assertEqual(bytearray([UNKNOWN] * 5), mask)


if __name__ == '__main__':
    unittest.main()
