#!/usr/bin/env python3.8

from copy import copy, deepcopy
from glob import fnmatch
import logging
import os
import sys
import unittest

SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, os.path.pardir)))

import nonogram
from nonogram.block import Block
from nonogram.column import Column
from nonogram.line import Line
from nonogram.row import Row
from nonogram.solution import Solution
from nonogram.solver import Solver

from nonogram.raster import Raster
from nonogram.raster import BLACK
from nonogram.raster import UNKNOWN
from nonogram.raster import WHITE


class TestSolver(unittest.TestCase):
    def __init__(self, *args):
        # logging.basicConfig(format='%(message)s', level=logging.DEBUG)

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

    # @unittest.skip('asdf')
    def test_model_integrity(self):
        """Test that no discrepacy occurs during the solving process."""
        err_in_model = []
        for test_file in [
            os.path.join(os.path.dirname(__file__), os.pardir, 'examples', f)
            for f in sorted(
                os.listdir(
                    os.path.
                    join(os.path.dirname(__file__), os.pardir, 'examples')
                )
            ) if fnmatch.fnmatch(f, '*.txt')
        ]:
            print(test_file)
            try:
                with open(test_file, 'rb') as fh:
                    raster = Raster(**Raster.parse_metadata(fh.readlines()))
                    Solver().solve(raster)
            except nonogram.DiscrepancyInModel as err:
                err_in_model.append(test_file)

        self.assertFalse(err_in_model)

    def test_fill_intersections(self):
        # if the line is solved (no UNKNOWN) then there's nothing to do...
        self.assertIsNone(
            Solver().fill_intersections(
                bytearray([BLACK, WHITE, BLACK]), Line(0, 0, [])
            )
        )

        # block fills the whole line (row or column)
        mask = bytearray([UNKNOWN, UNKNOWN, UNKNOWN])
        Solver().fill_intersections(
            mask, Line(0, 3, [Block(start=0, end=2, length=3)])
        )
        self.assertEqual(bytearray([BLACK, BLACK, BLACK]), mask)

        # 3 overlapping cells
        mask = bytearray([UNKNOWN] * 5)
        Solver().fill_intersections(
            mask, Line(0, 5, [Block(start=0, end=4, length=4)])
        )
        self.assertEqual(
            bytearray([UNKNOWN, BLACK, BLACK, BLACK, UNKNOWN]), mask
        )

        # one overlapping cell
        mask = bytearray([UNKNOWN] * 5)
        Solver().fill_intersections(
            mask, Line(0, 5, [Block(start=0, end=4, length=3)])
        )
        self.assertEqual(
            bytearray([UNKNOWN, UNKNOWN, BLACK, UNKNOWN, UNKNOWN]), mask
        )

        # no overlapping cell
        mask = bytearray([UNKNOWN] * 5)
        Solver().fill_intersections(
            mask, Line(0, 5, [Block(start=0, end=4, length=2)])
        )
        self.assertEqual(bytearray([UNKNOWN] * 5), mask)

    def test_check_spaces(self):
        # if the line is solved (no UNKNOWN) then there's nothing to do...
        self.assertIsNone(
            Solver()
            .check_spaces(bytearray([BLACK, WHITE, BLACK]), Line(0, 0, []))
        )

        # if there's no black run at all...
        mask = bytearray([UNKNOWN] * 4)
        Solver().check_spaces(mask, Line(size=4, idx=4, blocks=[]))
        self.assertEqual(bytearray([WHITE] * 4), mask)

        mask = bytearray([UNKNOWN] * 4)
        Solver().check_spaces(
            mask, Line(size=4, idx=4, blocks=[Block(start=0, end=3, length=0)])
        )
        self.assertEqual(bytearray([WHITE] * 4), mask)

        # start of the first block > 0 (1)
        mask = bytearray([UNKNOWN] * 4)
        Solver().check_spaces(
            mask, Line(size=4, idx=0, blocks=[Block(start=1, end=3, length=2)])
        )
        self.assertEqual(bytearray([WHITE] + [UNKNOWN] * 3), mask)

        # end of the last block < size - 1 (2)
        mask = bytearray([UNKNOWN] * 6)
        Solver().check_spaces(
            mask,
            Line(
                size=6,
                idx=0,
                blocks=[
                    Block(start=0, end=4, length=2),
                    Block(start=3, end=4, length=1)
                ]
            )
        )
        self.assertEqual(bytearray([UNKNOWN] * 5 + [WHITE]), mask)

        # gap betwen the end and start of two subsequent blocks (3)
        mask = bytearray([UNKNOWN] * 7)
        Solver().check_spaces(
            mask,
            Line(
                size=7,
                idx=0,
                blocks=[
                    Block(start=0, end=2, length=2),
                    Block(start=4, end=6, length=1)
                ]
            )
        )
        self.assertEqual(
            bytearray([UNKNOWN] * 3 + [WHITE] + [UNKNOWN] * 3), mask
        )

        # no gap as they're joint subsequent blocks
        mask = bytearray([UNKNOWN] * 7)
        Solver().check_spaces(
            mask,
            Line(
                size=7,
                idx=0,
                blocks=[
                    Block(start=0, end=3, length=2),
                    Block(start=4, end=6, length=1)
                ]
            )
        )
        self.assertEqual(bytearray([UNKNOWN] * 7), mask)

    def test_mark_white_cell_at_boundary(self):
        # if the line is solved (no UNKNOWN) then there's nothing to do...
        self.assertIsNone(
            Solver().mark_white_cell_at_boundary(
                bytearray([BLACK, WHITE, BLACK]), Line(0, 0, [])
            )
        )

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
        Solver().mark_white_cell_at_boundary(
            mask, Line(size=9, idx=0, blocks=blocks)
        )
        self.assertEqual(expected, mask)

        blocks = blocks[1:]
        # change mask at index 4 as all covering block has len 1
        expected = bytearray([UNKNOWN] * 4 + [WHITE] + [BLACK] + [UNKNOWN] * 3)
        Solver().mark_white_cell_at_boundary(
            mask, Line(size=9, idx=0, blocks=blocks)
        )
        self.assertEqual(expected, mask)

        # no change as mask at index 5 is not black
        mask = bytearray([UNKNOWN] * 9)
        expected = copy(mask)
        Solver().mark_white_cell_at_boundary(
            mask, Line(size=9, idx=0, blocks=blocks)
        )
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
        Solver().mark_white_cell_at_boundary(
            mask, Line(size=9, idx=0, blocks=blocks)
        )
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
        Solver().mark_white_cell_at_boundary(
            mask, Line(size=9, idx=0, blocks=blocks)
        )
        self.assertEqual(expected, mask)

        blocks = blocks[1:]
        # change mask at index 8 as all covering block has len 1
        expected = bytearray([UNKNOWN] * 7 + [BLACK, WHITE])
        Solver().mark_white_cell_at_boundary(
            mask, Line(size=9, idx=0, blocks=blocks)
        )
        self.assertEqual(expected, mask)

        # no change as mask at index 7 is not black
        mask = bytearray([UNKNOWN] * 9)
        expected = copy(mask)
        Solver().mark_white_cell_at_boundary(
            mask, Line(size=9, idx=0, blocks=blocks)
        )
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
        Solver().mark_white_cell_at_boundary(
            mask, Line(size=9, idx=0, blocks=blocks)
        )
        self.assertEqual(expected, mask)

    def test_covering_blocks(self):
        blocks = [
            Block(start=1, end=10, length=4),
            Block(start=6, end=9, length=4),
            Block(start=3, end=7, length=4),
            Block(start=2, end=4, length=4)
        ]

        covering_blocks = Solver()._covering_blocks(blocks, start=2)
        self.assertEqual(
            [Block(start=1, end=10, length=4),
             Block(start=2, end=4, length=4)], covering_blocks
        )

        covering_blocks = Solver()._covering_blocks(blocks, start=3, end=5)
        self.assertEqual(
            [Block(start=1, end=10, length=4),
             Block(start=3, end=7, length=4)], covering_blocks
        )

        covering_blocks = Solver()._covering_blocks(blocks, start=0)
        self.assertEqual([], covering_blocks)

    def test_get_black_runs(self):
        # mask = bytearray(map(ord, 'X.X  ..X..X. .X'))
        mask = bytearray(
            [
                BLACK, UNKNOWN, BLACK, WHITE, WHITE, UNKNOWN, UNKNOWN, BLACK,
                UNKNOWN, UNKNOWN, BLACK, UNKNOWN, WHITE, UNKNOWN, BLACK
            ]
        )
        expected = [
            Block(start=0, end=0, length=1),
            Block(start=2, end=2, length=1),
            Block(start=7, end=7, length=1),
            Block(start=10, end=10, length=1),
            Block(start=14, end=14, length=1)
        ]

        self.assertEqual(expected, Solver()._get_black_runs(mask))

        mask = bytearray(
            [
                UNKNOWN, BLACK, BLACK, WHITE, UNKNOWN, WHITE, UNKNOWN, UNKNOWN,
                BLACK, BLACK
            ]
        )
        expected = [
            Block(start=1, end=2, length=2),
            Block(start=8, end=9, length=2)
        ]
        self.assertEqual(expected, Solver()._get_black_runs(mask))

        mask = bytearray([BLACK, BLACK, BLACK, BLACK])
        expected = [Block(start=0, end=3, length=4)]
        self.assertEqual(expected, Solver()._get_black_runs(mask))

        mask = bytearray([WHITE, UNKNOWN, UNKNOWN, WHITE])
        self.assertEqual([], Solver()._get_black_runs(mask))

        mask = bytearray(
            [BLACK, WHITE, BLACK, WHITE] + [BLACK] * 4 + [UNKNOWN, BLACK]
        )
        expected = [
            Block(start=0, end=0, length=1),
            Block(start=2, end=2, length=1),
            Block(start=4, end=7, length=4),
            Block(start=9, end=9, length=1)
        ]
        self.assertEqual(expected, Solver()._get_black_runs(mask))

    def test_fill_cells_based_on_boundary(self):
        # if the line is solved (no UNKNOWN) then there's nothing to do...
        self.assertIsNone(
            Solver().fill_cells_based_on_boundary(
                bytearray([BLACK, WHITE, BLACK]), Line(0, 0, [])
            )
        )

        # fill one cell on the right
        blocks = [
            Block(start=0, end=7, length=3),
            Block(start=4, end=12, length=4)
        ]
        mask = bytearray(
            [UNKNOWN] * 3 + [WHITE] + [UNKNOWN] + [BLACK] + [UNKNOWN] * 7
        )
        expected = bytearray(
            [UNKNOWN] * 3 + [WHITE] + [UNKNOWN] + [BLACK] * 2 + [UNKNOWN] * 6
        )

        Solver().fill_cells_based_on_boundary(
            mask, Line(size=13, idx=0, blocks=blocks)
        )
        self.assertEqual(expected, mask)

        # fill one cell on the left
        blocks = [
            Block(start=5, end=12, length=3),
            Block(start=0, end=8, length=4)
        ]
        mask = bytearray(
            [UNKNOWN] * 7 + [BLACK] + [UNKNOWN] + [WHITE] + [UNKNOWN] * 3
        )
        expected = bytearray(
            [UNKNOWN] * 6 + [BLACK] * 2 + [UNKNOWN] + [WHITE] + [UNKNOWN] * 3
        )

        Solver().fill_cells_based_on_boundary(
            mask, Line(size=9, idx=0, blocks=blocks)
        )
        self.assertEqual(expected, mask)

        # fill one cell on the right, boundary is the wall
        blocks = [
            Block(start=0, end=3, length=3),
            Block(start=0, end=8, length=4)
        ]
        mask = bytearray([UNKNOWN] + [BLACK] + [UNKNOWN] * 7)
        expected = bytearray([UNKNOWN] + [BLACK] * 2 + [UNKNOWN] * 6)

        Solver().fill_cells_based_on_boundary(
            mask, Line(size=9, idx=0, blocks=blocks)
        )
        self.assertEqual(expected, mask)

        # fill one cell on the left boundary is the wall
        blocks = [
            Block(start=5, end=8, length=3),
            Block(start=0, end=8, length=4)
        ]
        mask = bytearray([UNKNOWN] * 7 + [BLACK] + [UNKNOWN])
        expected = bytearray([UNKNOWN] * 6 + [BLACK] * 2 + [UNKNOWN])

        Solver().fill_cells_based_on_boundary(
            mask, Line(size=9, idx=0, blocks=blocks)
        )
        self.assertEqual(expected, mask)

        # if there's a cell that isn't covered by a block
        blocks = [
            Block(start=0, end=4, length=3),
            Block(start=7, end=12, length=2)
        ]
        mask = bytearray(
            [UNKNOWN] * 3 + [WHITE] + [UNKNOWN] + [BLACK] + [UNKNOWN] * 7
        )

        Solver().fill_cells_based_on_boundary(
            mask, Line(size=13, idx=0, blocks=blocks)
        )
        # nothing should be changed
        self.assertEqual(mask, mask)

    def test_mark_boundary_if_possible(self):
        # if the line is solved (no UNKNOWN) then there's nothing to do...
        self.assertIsNone(
            Solver().mark_boundary_if_possible(
                bytearray([BLACK, WHITE, BLACK]), Line(0, 0, [])
            )
        )

        # fill one cell on the right
        blocks = [
            Block(start=0, end=3, length=1),
            Block(start=2, end=6, length=2),
            Block(start=5, end=9, length=2),
            Block(start=8, end=13, length=3)
        ]
        mask = bytearray([UNKNOWN] * 5 + [BLACK] * 2 + [UNKNOWN] * 7)
        expected = bytearray(
            [UNKNOWN] * 4 + [WHITE] + [BLACK] * 2 + [WHITE] + [UNKNOWN] * 6
        )

        Solver().mark_boundary_if_possible(
            mask, Line(size=9, idx=0, blocks=blocks)
        )
        self.assertEqual(expected, mask)

    def test_check_meta_consistency(self):
        meta = Line(
            size=10,
            idx=0,
            blocks=[
                Block(start=0, end=9, length=2),
                Block(start=0, end=9, length=3),
                Block(start=0, end=9, length=1)
            ]
        )

        expected = Line(
            size=10,
            idx=0,
            blocks=[
                Block(start=0, end=3, length=2),
                Block(start=3, end=7, length=3),
                Block(start=7, end=9, length=1)
            ]
        )

        Solver().check_meta_consistency(None, meta)
        self.assertEqual(expected, meta)

        meta = Line(size=10, idx=0, blocks=[Block(start=0, end=9, length=2)])
        expected = deepcopy(meta)
        Solver().check_meta_consistency(None, meta)
        self.assertEqual(expected, meta)

        meta = Line(
            size=10,
            idx=0,
            blocks=[
                Block(start=0, end=7, length=2),
                Block(start=2, end=8, length=3),
                Block(start=6, end=9, length=1)
            ]
        )
        expected = Line(
            size=10,
            idx=0,
            blocks=[
                Block(start=0, end=3, length=2),
                Block(start=3, end=7, length=3),
                Block(start=7, end=9, length=1)
            ]
        )

        Solver().check_meta_consistency(None, meta)
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
                Block(start=7, end=13, length=1)
            ]
        )
        expected = Line(
            size=14,
            idx=0,
            blocks=[
                Block(start=0, end=8, length=3),
                Block(start=8, end=11, length=2),
                Block(start=7, end=13, length=1)
            ]
        )

        Solver().narrow_boundaries(mask, meta)
        self.assertEqual(expected, meta)

        # '..XX...XX..'
        mask = bytearray(
            [UNKNOWN] * 2 + [BLACK] * 2 + [UNKNOWN] * 3 + [BLACK] * 2 +
            [UNKNOWN] * 2
        )

        meta = Line(
            size=11,
            idx=0,
            blocks=[
                Block(start=0, end=10, length=2),
                Block(start=0, end=10, length=3),
                Block(start=4, end=10, length=1)
            ]
        )
        expected = Line(
            size=11,
            idx=0,
            blocks=[
                Block(start=0, end=10, length=2),
                Block(start=0, end=10, length=3),
                Block(start=10, end=10, length=1)
            ]
        )

        Solver().narrow_boundaries(mask, meta)
        self.assertEqual(expected, meta)

        # '...XXX..XX.'
        mask = bytearray(
            [UNKNOWN] * 3 + [BLACK] * 3 + [UNKNOWN] * 2 + [BLACK] * 2 +
            [UNKNOWN]
        )

        meta = Line(
            size=11,
            idx=0,
            blocks=[
                Block(start=0, end=8, length=1),
                Block(start=2, end=10, length=4),
                Block(start=4, end=10, length=2)
            ]
        )
        expected = Line(
            size=11,
            idx=0,
            blocks=[
                Block(start=0, end=1, length=1),
                Block(start=2, end=10, length=4),
                Block(start=4, end=10, length=2)
            ]
        )

        Solver().narrow_boundaries(mask, meta)
        self.assertEqual(expected, meta)

    def test_fill_scattered_ranges(self):
        mask = bytearray(
            [UNKNOWN] * 4 + [BLACK] + [UNKNOWN] + [BLACK] + [UNKNOWN] * 6
        )
        meta = Line(
            size=13,
            idx=0,
            blocks=[
                Block(start=0, end=3, length=1),
                Block(start=2, end=8, length=4),
                Block(start=7, end=12, length=3)
            ]
        )
        expected_mask = bytearray([UNKNOWN] * 4 + [BLACK] * 3 + [UNKNOWN] * 6)
        expected_meta = Line(
            size=13,
            idx=0,
            blocks=[
                Block(start=0, end=3, length=1),
                Block(start=3, end=7, length=4),
                Block(start=7, end=12, length=3)
            ]
        )

        Solver().fill_scattered_ranges(mask, meta)
        self.assertEqual(expected_mask, mask)
        self.assertEqual(expected_meta, meta)

        # only 1 black run
        # '....XXX....'
        mask = bytearray([UNKNOWN] * 4 + [BLACK] * 3 + [UNKNOWN] * 4)

        meta = Line(size=11, idx=0, blocks=[Block(start=0, end=10, length=5)])

        expected_mask = copy(mask)

        expected_meta = Line(
            size=11, idx=0, blocks=[Block(start=2, end=8, length=5)]
        )

        Solver().fill_scattered_ranges(mask, meta)
        self.assertEqual(expected_mask, mask)
        self.assertEqual(expected_meta, meta)

        # '.... X .. '
        mask = bytearray(
            [UNKNOWN] * 4 + [WHITE] + [BLACK] + [WHITE] + [UNKNOWN] * 2 +
            [WHITE]
        )
        meta = Line(
            size=10,
            idx=0,
            blocks=[
                Block(start=0, end=5, length=1),
                Block(start=2, end=7, length=1),
                Block(start=4, end=9, length=1)
            ]
        )

        expected_mask = copy(mask)
        expected_meta = deepcopy(meta)
        Solver().fill_scattered_ranges(mask, meta)
        self.assertEqual(expected_mask, mask)
        self.assertEqual(expected_meta, meta)

        # bytearray(b'X  X .....')
        # 2 runs in one block's range but filling them would be longer
        # than the block's length
        mask = bytearray(
            [BLACK] + [WHITE] * 2 + [BLACK] + [WHITE] + [UNKNOWN] * 5
        )
        meta = Line(
            size=10,
            idx=0,
            blocks=[
                Block(start=0, end=3, length=1),
                Block(start=2, end=5, length=1),
                Block(start=5, end=7, length=1),
                Block(start=6, end=9, length=1),
            ]
        )
        expected_mask = copy(mask)
        expected_meta = deepcopy(meta)

        Solver().fill_scattered_ranges(mask, meta)
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
            ]
        )
        expected_mask = copy(mask)
        expected_meta = deepcopy(meta)

        Solver().fill_scattered_ranges(mask, meta)
        self.assertEqual(expected_mask, mask)
        self.assertEqual(expected_meta, meta)

    def test_get_non_white_runs(self):
        mask = bytearray(b'  X. .....')
        expected = [Block(start=2, end=3, length=2),
                    Block(start=5, end=9, length=5)]
        self.assertEqual(expected, Solver()._get_non_white_runs(mask))

        mask = bytearray(b'..X  .X  .')
        expected = [Block(start=0, end=2, length=3),
                    Block(start=5, end=6, length=2),
                    Block(start=9, end=9, length=1)]
        self.assertEqual(expected, Solver()._get_non_white_runs(mask))

        mask = bytearray(b'.    .X.X ')
        expected = [Block(start=0, end=0, length=1),
                    Block(start=5, end=8, length=4)]
        self.assertEqual(expected, Solver()._get_non_white_runs(mask))

        mask = bytearray(b'.    .X.  ')
        expected = [Block(start=0, end=0, length=1),
                    Block(start=5, end=7, length=3)]
        self.assertEqual(expected, Solver()._get_non_white_runs(mask))


if __name__ == '__main__':
    unittest.main()
