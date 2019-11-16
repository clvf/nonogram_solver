#!/usr/bin/env python3.8

import os
import sys
import unittest

SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, os.path.pardir)))

import nonogram
from nonogram.raster import BLACK
from nonogram.raster import Raster
from nonogram.raster import UNKNOWN
from nonogram.raster import WHITE
from nonogram.raster.block import Block
from nonogram.raster.line import Column
from nonogram.raster.line import Row


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
        self.assertParseMeta(
            {
                'col_meta': [
                    Column(4, 0, [Block(0, 4, 1)]),
                    Column(4, 1, [Block(0, 4, 3)]),
                    Column(4, 2, [Block(0, 4, 2)]),
                    Column(4, 3, [Block(0, 4, 3)]),
                    Column(4, 4, [Block(0, 4, 1)]),
                    Column(4, 5, [Block(0, 4, 1)]),
                    Column(4, 6, [Block(0, 4, 1)]),
                    Column(4, 7, [Block(0, 4, 3)]),
                    Column(4, 8, [Block(0, 4, 1), Block(0, 4, 1)]),
                    Column(4, 9, [Block(0, 4, 3)])
                ],
                'table': [
                    bytearray(b'..........'), bytearray(b'..........'),
                    bytearray(b'..........'), bytearray(b'..........'),
                    bytearray(b'..........')
                ],
                'row_meta': [
                    Row(10, 0, [Block(0, 9, 1)]),
                    Row(10, 1, [Block(0, 9, 1), Block(0, 9, 1)]),
                    Row(10, 2, [Block(0, 9, 1), Block(0, 9, 1)]), Row(
                        10, 3, [Block(0, 9, 3), Block(0, 9, 1), Block(0, 9, 1)]
                    ), Row(
                        10, 4, [Block(0, 9, 1), Block(0, 9, 1), Block(0, 9, 1)]
                    )
                ]
            }, spec
        )

    def assertParseMeta(self, expected_result, input_):
        raster_internals = Raster.parse_metadata(input_)
        print(Raster(**raster_internals))
        self.assertCountEqual(expected_result, raster_internals)

    def test_is_solved(self):
        raster = Raster(
            table=[bytearray((UNKNOWN for j in range(2))) for i in range(3)],
            row_meta=[],
            col_meta=[]
        )
        self.assertEqual(False, raster.is_solved())

        raster.table = [bytearray((BLACK for i in range(2)))]
        self.assertEqual(True, raster.is_solved())

        raster.table = [bytearray((WHITE for i in range(2)))]
        self.assertEqual(True, raster.is_solved())

        raster.table[0][0] = UNKNOWN
        self.assertEqual(False, raster.is_solved())

    def test_get_row(self):
        raster = Raster(
            table=[bytearray((UNKNOWN for j in range(2))) for i in range(3)],
            row_meta=[],
            col_meta=[]
        )
        raster.table[0] = bytearray([BLACK, WHITE])
        self.assertEqual(bytearray([BLACK, WHITE]), raster.get_row(0))

    def test_replace_row(self):
        raster = Raster(
            table=[bytearray((UNKNOWN for j in range(2))) for i in range(3)],
            row_meta=[],
            col_meta=[]
        )

        row = bytearray([BLACK, WHITE])
        raster._replace_row(row, 0)

        self.assertEqual(row, raster.get_row(0))
        self.assertNotEqual(row, raster.get_row(1))

    def test_get_col(self):
        raster = Raster(
            table=[bytearray((UNKNOWN for j in range(2))) for i in range(3)],
            row_meta=[],
            col_meta=[]
        )

        for i in range(3):
            raster.table[i][0] = BLACK
        self.assertEqual(bytearray([BLACK, BLACK, BLACK]), raster.get_col(0))

    def test_replace_col(self):
        raster = Raster(
            table=[bytearray((UNKNOWN for j in range(2))) for i in range(3)],
            row_meta=[],
            col_meta=[]
        )

        col = bytearray([BLACK, WHITE, BLACK])
        raster._replace_col(col, 1)

        self.assertEqual(col, raster.get_col(1))
        self.assertNotEqual(col, raster.get_col(0))

    def test_update_list(self):
        raster = Raster(table=[[]], row_meta=[], col_meta=[])
        rec = bytearray((BLACK, UNKNOWN, WHITE, UNKNOWN))
        mask = bytearray((UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN))

        # as mask is full with unknown, no change should be made
        self.assertEqual((rec, []), raster._update_list(rec, mask))

        mask = bytearray((UNKNOWN, WHITE, WHITE, BLACK))
        # change some cells and return their indexes
        self.assertEqual(
            (bytearray((BLACK, WHITE, WHITE, BLACK)), [1, 3]),
            raster._update_list(rec, mask)
        )

        # if rec and mask differ in "known" cells that's a discrepancy
        mask[0] = WHITE
        with self.assertRaises(nonogram.DiscrepancyInModel):
            raster._update_list(rec, mask)

    def test_update_row(self):
        raster = Raster(
            table=[bytearray((UNKNOWN for j in range(2))) for i in range(3)],
            row_meta=[],
            col_meta=[]
        )

        mask = bytearray([BLACK, WHITE])
        self.assertEqual([0, 1], raster.update_row(mask=mask, idx=0))
        self.assertEqual(mask, raster.get_row(0))

    def test_update_col(self):
        raster = Raster(
            table=[bytearray((UNKNOWN for j in range(2))) for i in range(3)],
            row_meta=[],
            col_meta=[]
        )

        mask = bytearray([BLACK, WHITE, UNKNOWN])
        self.assertEqual([0, 1], raster.update_col(mask=mask, idx=0))
        self.assertEqual(mask, raster.get_col(0))


if __name__ == '__main__':
    unittest.main()
