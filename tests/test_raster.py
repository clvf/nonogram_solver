#!/usr/bin/env python3

import os
import sys
import unittest

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from nonogram.raster import Raster
from nonogram.block import Block
from nonogram.column import Column
from nonogram.row import Row

from nonogram.raster import BLACK
from nonogram.raster import UNKNOWN
from nonogram.raster import WHITE


class TestRaster(unittest.TestCase):

    def test_parsemetadata_no_spec(self):
        with self.assertRaises(AttributeError):
            Raster.parse_metadata()

    def test_parsemetadata_valid(self):
        self.maxDiff = None
        spec = """10 5
1
3
2
3
1
1
1
3
1 1
3
1
1 1
8 1
3 1 1
1 1 1""".split("\n")
        self.assertParseMeta({
            'col_meta': [Column(4, 0, [Block(0, 4, 1)]),
                         Column(4, 1, [Block(0, 4, 3)]),
                         Column(4, 2, [Block(0, 4, 2)]),
                         Column(4, 3, [Block(0, 4, 3)]),
                         Column(4, 4, [Block(0, 4, 1)]),
                         Column(4, 5, [Block(0, 4, 1)]),
                         Column(4, 6, [Block(0, 4, 1)]),
                         Column(4, 7, [Block(0, 4, 3)]),
                         Column(4, 8, [Block(0, 4, 1), Block(0, 4, 1)]),
                         Column(4, 9, [Block(0, 4, 3)])],
            'table': [bytearray(b'..........'), bytearray(b'..........'),
                      bytearray(b'..........'), bytearray(b'..........'),
                      bytearray(b'..........')],
            'row_meta': [Row(10, 0, [Block(0, 9, 1)]),
                         Row(10, 1, [Block(0, 9, 1), Block(0, 9, 1)]),
                         Row(10, 2, [Block(0, 9, 1), Block(0, 9, 1)]),
                         Row(10, 3, [
                             Block(0, 9, 3), Block(0, 9, 1), Block(0, 9, 1)]),
                         Row(10, 4, [Block(0, 9, 1), Block(0, 9, 1), Block(0, 9, 1)])]
        }, spec)

    def assertParseMeta(self, expected_result, input_):
        self.assertCountEqual(expected_result, Raster.parse_metadata(input_))

    def test_is_solved(self):
        raster = Raster(table=[bytearray((UNKNOWN for j in range(2)))
                        for i in range(3)], row_meta=[], col_meta=[])
        self.assertEqual(False, raster.is_solved())

        raster.table = [bytearray((BLACK for i in range(2)))]
        self.assertEqual(True, raster.is_solved())

        raster.table = [bytearray((WHITE for i in range(2)))]
        self.assertEqual(True, raster.is_solved())

        raster.table[0][0] = UNKNOWN
        self.assertEqual(False, raster.is_solved())

    def test_get_row(self):
        raster = Raster(table=[bytearray((UNKNOWN for j in range(2)))
                        for i in range(3)], row_meta=[], col_meta=[])
        raster.table[0] = bytearray([BLACK, WHITE])
        self.assertEqual(bytearray([BLACK, WHITE]), raster.get_row(0))

    def test_replace_row(self):
        raster = Raster(table=[bytearray((UNKNOWN for j in range(2)))
                        for i in range(3)], row_meta=[], col_meta=[])

        row = bytearray([BLACK, WHITE])
        raster.replace_row(row, 0)

        self.assertEqual(row, raster.get_row(0))
        self.assertNotEqual(row, raster.get_row(1))

    def test_get_col(self):
        raster = Raster(table=[bytearray((UNKNOWN for j in range(2)))
                        for i in range(3)], row_meta=[], col_meta=[])

        for i in range(3):
            raster.table[i][0] = BLACK
        self.assertEqual(bytearray([BLACK, BLACK, BLACK]), raster.get_col(0))

    def test_replace_col(self):
        raster = Raster(table=[bytearray((UNKNOWN for j in range(2)))
                        for i in range(3)], row_meta=[], col_meta=[])

        col = bytearray([BLACK, WHITE, BLACK])
        raster.replace_col(col, 1)

        self.assertEqual(col, raster.get_col(1))
        self.assertNotEqual(col, raster.get_col(0))


if __name__ == '__main__':
    unittest.main()
