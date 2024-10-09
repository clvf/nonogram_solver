#!/usr/bin/env python

from copy import copy, deepcopy
import os
import unittest

# pylint: disable=wrong-import-position,missing-docstring
from nonogrampy.raster import BLACK
from nonogrampy.raster import UNKNOWN
from nonogrampy.raster import WHITE
from nonogrampy.raster.block import Block
from nonogrampy.raster.line import Line

from nonogrampy.rules import r3


class TestR3(unittest.TestCase):
    def test_fill_scattered_ranges(self):
        mask = bytearray([UNKNOWN] * 4 + [BLACK] + [UNKNOWN] + [BLACK] + [UNKNOWN] * 6)
        meta = Line(
            size=13,
            idx=0,
            blocks=[
                Block(start=0, end=3, length=1),
                Block(start=2, end=8, length=4),
                Block(start=7, end=12, length=3),
            ],
        )
        expected_mask = bytearray([UNKNOWN] * 4 + [BLACK] * 3 + [UNKNOWN] * 6)
        expected_meta = Line(
            size=13,
            idx=0,
            blocks=[
                Block(start=0, end=3, length=1),
                Block(start=3, end=7, length=4),
                Block(start=7, end=12, length=3),
            ],
        )

        r3.fill_scattered_ranges(mask, meta)
        self.assertEqual(expected_mask, mask)
        self.assertEqual(expected_meta, meta)

        # only 1 black run
        # '....XXX....'
        mask = bytearray([UNKNOWN] * 4 + [BLACK] * 3 + [UNKNOWN] * 4)

        meta = Line(size=11, idx=0, blocks=[Block(start=0, end=10, length=5)])

        expected_mask = copy(mask)

        expected_meta = Line(size=11, idx=0, blocks=[Block(start=2, end=8, length=5)])

        r3.fill_scattered_ranges(mask, meta)
        self.assertEqual(expected_mask, mask)
        self.assertEqual(expected_meta, meta)

        # '.... X .. '
        mask = bytearray(
            [UNKNOWN] * 4 + [WHITE] + [BLACK] + [WHITE] + [UNKNOWN] * 2 + [WHITE]
        )
        meta = Line(
            size=10,
            idx=0,
            blocks=[
                Block(start=0, end=5, length=1),
                Block(start=2, end=7, length=1),
                Block(start=4, end=9, length=1),
            ],
        )

        expected_mask = copy(mask)
        expected_meta = deepcopy(meta)
        r3.fill_scattered_ranges(mask, meta)
        self.assertEqual(expected_mask, mask)
        self.assertEqual(expected_meta, meta)

        # bytearray(b'X  X .....')
        # 2 runs in one block's range but filling them would be longer
        # than the block's length
        mask = bytearray([BLACK] + [WHITE] * 2 + [BLACK] + [WHITE] + [UNKNOWN] * 5)
        meta = Line(
            size=10,
            idx=0,
            blocks=[
                Block(start=0, end=3, length=1),
                Block(start=2, end=5, length=1),
                Block(start=5, end=7, length=1),
                Block(start=6, end=9, length=1),
            ],
        )
        expected_mask = copy(mask)
        expected_meta = deepcopy(meta)

        r3.fill_scattered_ranges(mask, meta)
        self.assertEqual(expected_mask, mask)
        self.assertEqual(expected_meta, meta)

        # bytearray(b'  X..XX...')
        mask = bytearray(
            [WHITE] * 2 + [BLACK] + [UNKNOWN] * 2 + [BLACK] * 2 + [UNKNOWN] * 3
        )
        meta = Line(
            size=10,
            idx=0,
            blocks=[
                Block(start=0, end=3, length=1),
                Block(start=2, end=9, length=5),
            ],
        )
        expected_mask = copy(mask)
        expected_meta = deepcopy(meta)

        r3.fill_scattered_ranges(mask, meta)
        self.assertEqual(expected_mask, mask)
        self.assertEqual(expected_meta, meta)


if __name__ == "__main__":
    unittest.main()
