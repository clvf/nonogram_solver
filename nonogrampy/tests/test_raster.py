#!/usr/bin/env python

import io
import os
import unittest

# pylint: disable=wrong-import-position
import nonogrampy
from nonogrampy.raster import BLACK
from nonogrampy.raster import Raster
from nonogrampy.raster import UNKNOWN
from nonogrampy.raster import WHITE
from nonogrampy.raster.block import Block
from nonogrampy.raster.line import Column
from nonogrampy.raster.line import Row


class TestRaster(unittest.TestCase):
    # pylint: disable=protected-access,missing-docstring
    def test_from_file(self):
        spec = io.StringIO(
            """
10 5

# rows:
1
1 1
8 1
3 1 1
1 1 1
  

	
# columns:
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
"""
        )
        raster = Raster.from_file(spec)
        self.assertEqual(
            raster.col_meta,
            [
                Column(5, 0, [Block(0, 4, 1)]),
                Column(5, 1, [Block(0, 4, 3)]),
                Column(5, 2, [Block(0, 4, 2)]),
                Column(5, 3, [Block(0, 4, 3)]),
                Column(5, 4, [Block(0, 4, 1)]),
                Column(5, 5, [Block(0, 4, 1)]),
                Column(5, 6, [Block(0, 4, 1)]),
                Column(5, 7, [Block(0, 4, 3)]),
                Column(5, 8, [Block(0, 4, 1), Block(0, 4, 1)]),
                Column(5, 9, [Block(0, 4, 3)]),
            ],
        )
        self.assertEqual(
            raster.table,
            [
                bytearray(b".........."),
                bytearray(b".........."),
                bytearray(b".........."),
                bytearray(b".........."),
                bytearray(b".........."),
            ],
        )
        self.assertEqual(
            raster.row_meta,
            [
                Row(10, 0, [Block(0, 9, 1)]),
                Row(10, 1, [Block(0, 9, 1), Block(0, 9, 1)]),
                Row(10, 2, [Block(0, 9, 8), Block(0, 9, 1)]),
                Row(10, 3, [Block(0, 9, 3), Block(0, 9, 1), Block(0, 9, 1)]),
                Row(10, 4, [Block(0, 9, 1), Block(0, 9, 1), Block(0, 9, 1)]),
            ],
        )

    def test_is_solved(self):
        raster = Raster(
            table=[bytearray((UNKNOWN for j in range(2))) for i in range(3)],
            row_meta=[],
            col_meta=[],
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
            col_meta=[],
        )
        raster.table[0] = bytearray([BLACK, WHITE])
        self.assertEqual(bytearray([BLACK, WHITE]), raster.get_row(0))

    def test_replace_row(self):
        raster = Raster(
            table=[bytearray((UNKNOWN for j in range(2))) for i in range(3)],
            row_meta=[],
            col_meta=[],
        )

        row = bytearray([BLACK, WHITE])
        raster._replace_row(row, 0)

        self.assertEqual(row, raster.get_row(0))
        self.assertNotEqual(row, raster.get_row(1))

    def test_get_col(self):
        raster = Raster(
            table=[bytearray((UNKNOWN for j in range(2))) for i in range(3)],
            row_meta=[],
            col_meta=[],
        )

        for i in range(3):
            raster.table[i][0] = BLACK
        self.assertEqual(bytearray([BLACK, BLACK, BLACK]), raster.get_col(0))

    def test_replace_col(self):
        raster = Raster(
            table=[bytearray((UNKNOWN for j in range(2))) for i in range(3)],
            row_meta=[],
            col_meta=[],
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
            raster._update_list(rec, mask),
        )

        # if rec and mask differ in "known" cells that's a discrepancy
        mask[0] = WHITE
        with self.assertRaises(nonogrampy.DiscrepancyInModel):
            raster._update_list(rec, mask)

    def test_update_row(self):
        raster = Raster(
            table=[bytearray((UNKNOWN for j in range(2))) for i in range(3)],
            row_meta=[],
            col_meta=[],
        )

        mask = bytearray([BLACK, WHITE])
        self.assertEqual([0, 1], raster.update_row(mask=mask, idx=0))
        self.assertEqual(mask, raster.get_row(0))

    def test_update_col(self):
        raster = Raster(
            table=[bytearray((UNKNOWN for j in range(2))) for i in range(3)],
            row_meta=[],
            col_meta=[],
        )

        mask = bytearray([BLACK, WHITE, UNKNOWN])
        self.assertEqual([0, 1], raster.update_col(mask=mask, idx=0))
        self.assertEqual(mask, raster.get_col(0))


if __name__ == "__main__":
    unittest.main()
