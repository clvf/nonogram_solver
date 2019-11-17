#!/usr/bin/env python3.8

import os
import sys
import unittest

SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(
    os.path.normpath(os.path.join(SCRIPT_DIR, os.path.pardir, os.path.pardir)))

# pylint: disable=wrong-import-position
from nonogram.raster import BLACK
from nonogram.raster import UNKNOWN
from nonogram.raster import WHITE
from nonogram.raster.block import Block

from nonogram import rules


class TestRules(unittest.TestCase):
    # pylint: disable=protected-access
    def test_covering_blocks(self):
        blocks = [
            Block(start=1, end=10, length=4),
            Block(start=6, end=9, length=4),
            Block(start=3, end=7, length=4),
            Block(start=2, end=4, length=4)
        ]

        covering_blocks = rules._covering_blocks(blocks, start=2)
        self.assertEqual([
            Block(start=1, end=10, length=4),
            Block(start=2, end=4, length=4)
        ], covering_blocks)

        covering_blocks = rules._covering_blocks(blocks, start=3, end=5)
        self.assertEqual([
            Block(start=1, end=10, length=4),
            Block(start=3, end=7, length=4)
        ], covering_blocks)

        covering_blocks = rules._covering_blocks(blocks, start=0)
        self.assertEqual([], covering_blocks)

    def test_get_black_runs(self):
        # mask = bytearray(map(ord, 'X.X  ..X..X. .X'))
        mask = bytearray([
            BLACK, UNKNOWN, BLACK, WHITE, WHITE, UNKNOWN, UNKNOWN, BLACK,
            UNKNOWN, UNKNOWN, BLACK, UNKNOWN, WHITE, UNKNOWN, BLACK
        ])
        expected = [
            Block(start=0, end=0, length=1),
            Block(start=2, end=2, length=1),
            Block(start=7, end=7, length=1),
            Block(start=10, end=10, length=1),
            Block(start=14, end=14, length=1)
        ]

        self.assertEqual(expected, rules._get_black_runs(mask))

        mask = bytearray([
            UNKNOWN, BLACK, BLACK, WHITE, UNKNOWN, WHITE, UNKNOWN, UNKNOWN,
            BLACK, BLACK
        ])
        expected = [
            Block(start=1, end=2, length=2),
            Block(start=8, end=9, length=2)
        ]
        self.assertEqual(expected, rules._get_black_runs(mask))

        mask = bytearray([BLACK, BLACK, BLACK, BLACK])
        expected = [Block(start=0, end=3, length=4)]
        self.assertEqual(expected, rules._get_black_runs(mask))

        mask = bytearray([WHITE, UNKNOWN, UNKNOWN, WHITE])
        self.assertEqual([], rules._get_black_runs(mask))

        mask = bytearray(
            [BLACK, WHITE, BLACK, WHITE] + [BLACK] * 4 + [UNKNOWN, BLACK])
        expected = [
            Block(start=0, end=0, length=1),
            Block(start=2, end=2, length=1),
            Block(start=4, end=7, length=4),
            Block(start=9, end=9, length=1)
        ]
        self.assertEqual(expected, rules._get_black_runs(mask))

    def test_get_non_white_runs(self):
        mask = bytearray(b'  X. .....')
        expected = [
            Block(start=2, end=3, length=2),
            Block(start=5, end=9, length=5)
        ]
        self.assertEqual(expected, rules._get_non_white_runs(mask))

        mask = bytearray(b'..X  .X  .')
        expected = [
            Block(start=0, end=2, length=3),
            Block(start=5, end=6, length=2),
            Block(start=9, end=9, length=1)
        ]
        self.assertEqual(expected, rules._get_non_white_runs(mask))

        mask = bytearray(b'.    .X.X ')
        expected = [
            Block(start=0, end=0, length=1),
            Block(start=5, end=8, length=4)
        ]
        self.assertEqual(expected, rules._get_non_white_runs(mask))

        mask = bytearray(b'.    .X.  ')
        expected = [
            Block(start=0, end=0, length=1),
            Block(start=5, end=7, length=3)
        ]
        self.assertEqual(expected, rules._get_non_white_runs(mask))


if __name__ == '__main__':
    unittest.main()
