#!/usr/bin/env python3.8

from copy import deepcopy
import os
import sys
import unittest

SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
)
sys.path.append(
    os.path.normpath(os.path.join(SCRIPT_DIR, os.path.pardir, os.path.pardir))
)

# pylint: disable=wrong-import-position
from nonogram.raster import BLACK
from nonogram.raster import UNKNOWN
from nonogram.raster.block import Block
from nonogram.raster.line import Line

from nonogram.rules import r2


class TestR2(unittest.TestCase):
    # pylint: disable=missing-docstring
    def test_check_meta_consistency(self):
        meta = Line(
            size=10,
            idx=0,
            blocks=[
                Block(start=0, end=9, length=2),
                Block(start=0, end=9, length=3),
                Block(start=0, end=9, length=1),
            ],
        )

        expected = Line(
            size=10,
            idx=0,
            blocks=[
                Block(start=0, end=3, length=2),
                Block(start=3, end=7, length=3),
                Block(start=7, end=9, length=1),
            ],
        )

        r2.check_meta_consistency(None, meta)
        self.assertEqual(expected, meta)

        meta = Line(size=10, idx=0, blocks=[Block(start=0, end=9, length=2)])
        expected = deepcopy(meta)
        r2.check_meta_consistency(None, meta)
        self.assertEqual(expected, meta)

        meta = Line(
            size=10,
            idx=0,
            blocks=[
                Block(start=0, end=7, length=2),
                Block(start=2, end=8, length=3),
                Block(start=6, end=9, length=1),
            ],
        )
        expected = Line(
            size=10,
            idx=0,
            blocks=[
                Block(start=0, end=3, length=2),
                Block(start=3, end=7, length=3),
                Block(start=7, end=9, length=1),
            ],
        )

        r2.check_meta_consistency(None, meta)
        self.assertEqual(expected, meta)

    def test_look_for_trailing_white_cell(self):
        pass

    def test_narrow_boundaries(self):
        mask = bytearray(
            [UNKNOWN] * 4 + [BLACK] * 3 + [UNKNOWN] * 4 + [BLACK] + [UNKNOWN] * 2
        )
        meta = Line(
            size=14,
            idx=0,
            blocks=[
                Block(start=0, end=8, length=3),
                Block(start=4, end=11, length=2),
                Block(start=7, end=13, length=1),
            ],
        )
        expected = Line(
            size=14,
            idx=0,
            blocks=[
                Block(start=0, end=8, length=3),
                Block(start=8, end=11, length=2),
                Block(start=7, end=13, length=1),
            ],
        )

        r2.narrow_boundaries(mask, meta)
        self.assertEqual(expected, meta)

        # '..XX...XX..'
        mask = bytearray(
            [UNKNOWN] * 2 + [BLACK] * 2 + [UNKNOWN] * 3 + [BLACK] * 2 + [UNKNOWN] * 2
        )

        meta = Line(
            size=11,
            idx=0,
            blocks=[
                Block(start=0, end=10, length=2),
                Block(start=0, end=10, length=3),
                Block(start=4, end=10, length=1),
            ],
        )
        expected = Line(
            size=11,
            idx=0,
            blocks=[
                Block(start=0, end=10, length=2),
                Block(start=0, end=10, length=3),
                Block(start=10, end=10, length=1),
            ],
        )

        r2.narrow_boundaries(mask, meta)
        self.assertEqual(expected, meta)

        # '...XXX..XX.'
        mask = bytearray(
            [UNKNOWN] * 3 + [BLACK] * 3 + [UNKNOWN] * 2 + [BLACK] * 2 + [UNKNOWN]
        )

        meta = Line(
            size=11,
            idx=0,
            blocks=[
                Block(start=0, end=8, length=1),
                Block(start=2, end=10, length=4),
                Block(start=4, end=10, length=2),
            ],
        )
        expected = Line(
            size=11,
            idx=0,
            blocks=[
                Block(start=0, end=1, length=1),
                Block(start=2, end=10, length=4),
                Block(start=4, end=10, length=2),
            ],
        )

        r2.narrow_boundaries(mask, meta)
        self.assertEqual(expected, meta)


if __name__ == "__main__":
    unittest.main()
