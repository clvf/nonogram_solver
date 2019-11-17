#!/usr/bin/env python3.8

from copy import copy
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
from nonogram.raster.line import Line

from nonogram.rules import r1


class TestR1(unittest.TestCase):
    # pylint: disable=missing-docstring
    def test_fill_intersections(self):
        # if the line is solved (no UNKNOWN) then there's nothing to do...
        self.assertIsNone(
            r1.fill_intersections(
                bytearray([BLACK, WHITE, BLACK]), Line(0, 0, [])))

        # block fills the whole line (row or column)
        mask = bytearray([UNKNOWN, UNKNOWN, UNKNOWN])
        r1.fill_intersections(mask,
                              Line(0, 3, [Block(start=0, end=2, length=3)]))
        self.assertEqual(bytearray([BLACK, BLACK, BLACK]), mask)

        # 3 overlapping cells
        mask = bytearray([UNKNOWN] * 5)
        r1.fill_intersections(mask,
                              Line(0, 5, [Block(start=0, end=4, length=4)]))
        self.assertEqual(
            bytearray([UNKNOWN, BLACK, BLACK, BLACK, UNKNOWN]), mask)

        # one overlapping cell
        mask = bytearray([UNKNOWN] * 5)
        r1.fill_intersections(mask,
                              Line(0, 5, [Block(start=0, end=4, length=3)]))
        self.assertEqual(
            bytearray([UNKNOWN, UNKNOWN, BLACK, UNKNOWN, UNKNOWN]), mask)

        # no overlapping cell
        mask = bytearray([UNKNOWN] * 5)
        r1.fill_intersections(mask,
                              Line(0, 5, [Block(start=0, end=4, length=2)]))
        self.assertEqual(bytearray([UNKNOWN] * 5), mask)

    def test_check_spaces(self):
        # if the line is solved (no UNKNOWN) then there's nothing to do...
        self.assertIsNone(
            r1.check_spaces(bytearray([BLACK, WHITE, BLACK]), Line(0, 0, [])))

        # if there's no black run at all...
        mask = bytearray([UNKNOWN] * 4)
        r1.check_spaces(mask, Line(size=4, idx=4, blocks=[]))
        self.assertEqual(bytearray([WHITE] * 4), mask)

        mask = bytearray([UNKNOWN] * 4)
        r1.check_spaces(mask,
                        Line(size=4, idx=4,
                             blocks=[Block(start=0, end=3, length=0)]))
        self.assertEqual(bytearray([WHITE] * 4), mask)

        # start of the first block > 0 (1)
        mask = bytearray([UNKNOWN] * 4)
        r1.check_spaces(mask,
                        Line(size=4, idx=0,
                             blocks=[Block(start=1, end=3, length=2)]))
        self.assertEqual(bytearray([WHITE] + [UNKNOWN] * 3), mask)

        # end of the last block < size - 1 (2)
        mask = bytearray([UNKNOWN] * 6)
        r1.check_spaces(mask,
                        Line(size=6, idx=0, blocks=[
                            Block(start=0, end=4, length=2),
                            Block(start=3, end=4, length=1)
                        ]))
        self.assertEqual(bytearray([UNKNOWN] * 5 + [WHITE]), mask)

        # gap betwen the end and start of two subsequent blocks (3)
        mask = bytearray([UNKNOWN] * 7)
        r1.check_spaces(mask,
                        Line(size=7, idx=0, blocks=[
                            Block(start=0, end=2, length=2),
                            Block(start=4, end=6, length=1)
                        ]))
        self.assertEqual(
            bytearray([UNKNOWN] * 3 + [WHITE] + [UNKNOWN] * 3), mask)

        # no gap as they're joint subsequent blocks
        mask = bytearray([UNKNOWN] * 7)
        r1.check_spaces(mask,
                        Line(size=7, idx=0, blocks=[
                            Block(start=0, end=3, length=2),
                            Block(start=4, end=6, length=1)
                        ]))
        self.assertEqual(bytearray([UNKNOWN] * 7), mask)

    def test_mark_white_cell_at_boundary(self):
        # if the line is solved (no UNKNOWN) then there's nothing to do...
        self.assertIsNone(
            r1.mark_white_cell_at_boundary(
                bytearray([BLACK, WHITE, BLACK]), Line(0, 0, [])))

        # START
        blocks = [
            Block(start=1, end=8, length=4),
            Block(start=5, end=8, length=2),
            Block(start=3, end=8, length=1),
            Block(start=0, end=8, length=1)
        ]
        mask = bytearray([UNKNOWN] * 5 + [BLACK] + [UNKNOWN] * 3)
        expected = copy(mask)
        # no change as not all covering block has len 1
        r1.mark_white_cell_at_boundary(mask, Line(size=9, idx=0,
                                                  blocks=blocks))
        self.assertEqual(expected, mask)

        blocks = blocks[1:]
        # change mask at index 4 as all covering block has len 1
        expected = bytearray([UNKNOWN] * 4 + [WHITE] + [BLACK] + [UNKNOWN] * 3)
        r1.mark_white_cell_at_boundary(mask, Line(size=9, idx=0,
                                                  blocks=blocks))
        self.assertEqual(expected, mask)

        # no change as mask at index 5 is not black
        mask = bytearray([UNKNOWN] * 9)
        expected = copy(mask)
        r1.mark_white_cell_at_boundary(mask, Line(size=9, idx=0,
                                                  blocks=blocks))
        self.assertEqual(expected, mask)

        # if start index == 0 then nothing should be done obviously
        blocks = [
            Block(start=0, end=4, length=2),
            Block(start=0, end=8, length=1),
            Block(start=0, end=3, length=1)
        ]
        mask = bytearray([BLACK] + [UNKNOWN] * 8)
        expected = copy(mask)
        # no change as not all covering block has len 1
        r1.mark_white_cell_at_boundary(mask, Line(size=9, idx=0,
                                                  blocks=blocks))
        self.assertEqual(expected, mask)

        # END
        blocks = [
            Block(start=1, end=8, length=4),
            Block(start=5, end=7, length=2),
            Block(start=3, end=8, length=1),
            Block(start=3, end=7, length=1)
        ]
        mask = bytearray([UNKNOWN] * 7 + [BLACK] + [UNKNOWN])
        expected = copy(mask)
        # no change as not all covering block has len 1
        r1.mark_white_cell_at_boundary(mask, Line(size=9, idx=0,
                                                  blocks=blocks))
        self.assertEqual(expected, mask)

        blocks = blocks[1:]
        # change mask at index 8 as all covering block has len 1
        expected = bytearray([UNKNOWN] * 7 + [BLACK, WHITE])
        r1.mark_white_cell_at_boundary(mask, Line(size=9, idx=0,
                                                  blocks=blocks))
        self.assertEqual(expected, mask)

        # no change as mask at index 7 is not black
        mask = bytearray([UNKNOWN] * 9)
        expected = copy(mask)
        r1.mark_white_cell_at_boundary(mask, Line(size=9, idx=0,
                                                  blocks=blocks))
        self.assertEqual(expected, mask)

        # if end index == last index then nothing should be done obviously
        blocks = [
            Block(start=5, end=8, length=2),
            Block(start=3, end=8, length=1),
            Block(start=3, end=7, length=1)
        ]
        mask = bytearray([UNKNOWN] * 8 + [BLACK])
        expected = copy(mask)
        # no change as not all covering block has len 1
        r1.mark_white_cell_at_boundary(mask, Line(size=9, idx=0,
                                                  blocks=blocks))
        self.assertEqual(expected, mask)

    def test_fill_cells_based_on_boundary(self):
        # if the line is solved (no UNKNOWN) then there's nothing to do...
        self.assertIsNone(
            r1.fill_cells_based_on_boundary(
                bytearray([BLACK, WHITE, BLACK]), Line(0, 0, [])))

        # fill one cell on the right
        blocks = [
            Block(start=0, end=7, length=3),
            Block(start=4, end=12, length=4)
        ]
        mask = bytearray(
            [UNKNOWN] * 3 + [WHITE] + [UNKNOWN] + [BLACK] + [UNKNOWN] * 7)
        expected = bytearray(
            [UNKNOWN] * 3 + [WHITE] + [UNKNOWN] + [BLACK] * 2 + [UNKNOWN] * 6)

        r1.fill_cells_based_on_boundary(mask,
                                        Line(size=13, idx=0, blocks=blocks))
        self.assertEqual(expected, mask)

        # fill one cell on the left
        blocks = [
            Block(start=5, end=12, length=3),
            Block(start=0, end=8, length=4)
        ]
        mask = bytearray(
            [UNKNOWN] * 7 + [BLACK] + [UNKNOWN] + [WHITE] + [UNKNOWN] * 3)
        expected = bytearray(
            [UNKNOWN] * 6 + [BLACK] * 2 + [UNKNOWN] + [WHITE] + [UNKNOWN] * 3)

        r1.fill_cells_based_on_boundary(mask, Line(size=9, idx=0,
                                                   blocks=blocks))
        self.assertEqual(expected, mask)

        # fill one cell on the right, boundary is the wall
        blocks = [
            Block(start=0, end=3, length=3),
            Block(start=0, end=8, length=4)
        ]
        mask = bytearray([UNKNOWN] + [BLACK] + [UNKNOWN] * 7)
        expected = bytearray([UNKNOWN] + [BLACK] * 2 + [UNKNOWN] * 6)

        r1.fill_cells_based_on_boundary(mask, Line(size=9, idx=0,
                                                   blocks=blocks))
        self.assertEqual(expected, mask)

        # fill one cell on the left boundary is the wall
        blocks = [
            Block(start=5, end=8, length=3),
            Block(start=0, end=8, length=4)
        ]
        mask = bytearray([UNKNOWN] * 7 + [BLACK] + [UNKNOWN])
        expected = bytearray([UNKNOWN] * 6 + [BLACK] * 2 + [UNKNOWN])

        r1.fill_cells_based_on_boundary(mask, Line(size=9, idx=0,
                                                   blocks=blocks))
        self.assertEqual(expected, mask)

        # if there's a cell that isn't covered by a block
        blocks = [
            Block(start=0, end=4, length=3),
            Block(start=7, end=12, length=2)
        ]
        mask = bytearray(
            [UNKNOWN] * 3 + [WHITE] + [UNKNOWN] + [BLACK] + [UNKNOWN] * 7)

        r1.fill_cells_based_on_boundary(mask,
                                        Line(size=13, idx=0, blocks=blocks))
        # nothing should be changed
        self.assertEqual(mask, mask)

    def test_mark_boundary_if_possible(self):
        # if the line is solved (no UNKNOWN) then there's nothing to do...
        self.assertIsNone(
            r1.mark_boundary_if_possible(
                bytearray([BLACK, WHITE, BLACK]), Line(0, 0, [])))

        # fill one cell on the right
        blocks = [
            Block(start=0, end=3, length=1),
            Block(start=2, end=6, length=2),
            Block(start=5, end=9, length=2),
            Block(start=8, end=13, length=3)
        ]
        mask = bytearray([UNKNOWN] * 5 + [BLACK] * 2 + [UNKNOWN] * 7)
        expected = bytearray(
            [UNKNOWN] * 4 + [WHITE] + [BLACK] * 2 + [WHITE] + [UNKNOWN] * 6)

        r1.mark_boundary_if_possible(mask, Line(size=9, idx=0, blocks=blocks))
        self.assertEqual(expected, mask)


if __name__ == '__main__':
    unittest.main()
