"""
Implementation of the logic to solve the nonogram.
"""

from .raster import BLACK
from .raster import UNKNOWN
from .raster import WHITE
from .solution import Solution
import logging


# class FoundSolution(Exception):
#
#    def __init__(self, value):
#        self.value = value
#
#    def __str__(self):
#        return str(self.value)


class Solver(object):

    def solve(self, raster):
        """Does a rule based elimination on the raster object and returns a
        solution (object) if there's any and None otherwise."""
        # just let the first iteration of while going
        cells_changed = True
        while(cells_changed):
            cells_changed = False
            for meta in raster.row_meta:
                mask = raster.get_row(meta.idx)

                self.linesolve(mask, meta)

                if raster.update_row(mask=mask, idx=meta.idx):
                    cells_changed = True

            for meta in raster.col_meta:
                mask = raster.get_col(meta.idx)

                self.linesolve(mask, meta)

                if raster.update_col(mask=mask, idx=meta.idx):
                    cells_changed = True

        if raster.is_solved():
            return Solution(raster.table)

        return None

    def linesolve(self, mask, meta):
        """Rule based elimination on the received parameters."""
        self.fill_intersections(mask, meta)
        self.check_spaces(mask, meta)
        self.mark_white_cell_at_boundary(mask, meta)

    def fill_intersections(self, mask, meta):
        """Rule 1.1:

        for each black run j, cell ci will be colored when
        rj.s+u <= i <= rj.e - u
        where u = (rj.e - rj.s + 1) -LBj
        and LBj is the length of a black run j
        """
        # return if this line already "solved" completely
        if UNKNOWN not in mask:
            return

        debug_prefix = "R1.1 fill_intersections: {!s} -> ".format(mask)
        debug_suffix = ", {!s}".format(meta)

        for block in meta.blocks:
            u = (block.end - block.start + 1) - block.length
            assert u >= 0, "u: " + str(u) + " blk: " + str(block)

            lb = block.start + u  # lower bound
            ub = block.end - u + 1  # upper bound
            if lb < ub:
                mask[lb:ub] = [BLACK] * (ub - lb)
        logging.debug(debug_prefix + "{!s}".format(mask) + debug_suffix)

    def check_spaces(self, mask, meta):
        """Rule 1.2:
        When a cell does not belong to the run range of any black run, the
        cell should be left empty.

        For each cell ci, it will be left empty, if one of the following
        three conditions is satisfied:
        (1) 0 <= i < r1.s
        (2) rk.e < i < n
        (3) rj.e < i < rj+1.s for some j, 1 <= j < k
        """
        # return if this line already "solved" completely
        if UNKNOWN not in mask:
            return

        debug_prefix = "R1.2 check_spaces: {!s} -> ".format(mask)
        debug_suffix = ", {!s}".format(meta)

        # if there are no black runs in the row/col at all...
        if len(meta.blocks) == 0 or meta.blocks[0].length == 0:
            mask[:] = [WHITE] * meta.size
        else:
            # (1)
            for i in range(meta.blocks[0].start):
                mask[i] = WHITE
            # (2)
            for i in range(meta.blocks[-1].end + 1, meta.size):
                mask[i] = WHITE
            # (3)
            for j in range(len(meta.blocks) - 1):
                for i in range(meta.blocks[j].end + 1, meta.blocks[j + 1].start):
                    mask[i] = WHITE

        logging.debug(debug_prefix + "{!s}".format(mask) + debug_suffix)

    def mark_white_cell_at_boundary(self, mask, meta):
        """Rule 1.3:

        For each black runj, j = 1,...,k
        (1) If the lengths of all black run i covering cell rj.s with i != j
            are all one, cell rj.s - 1 will be left empty
        (2) If the lengths of all black run i covering rj.e with i != j
            are all one, cell rj.e + 1 will be left empty
        """
        # return if this line already "solved" completely
        if UNKNOWN not in mask:
            return

        debug_prefix = "R1.2 check_spaces: {!s} -> ".format(mask)
        debug_suffix = ", {!s}".format(meta)

        for idx in range(len(meta.blocks)):
            block = meta.blocks[idx]
            blocks_wo_this = [meta.blocks[i]
                              for i in range(len(meta.blocks)) if idx != i]

            # if the start of the block is BLACK and the preceding cell is
            # UNKNOWN
            if mask[block.start] == BLACK and block.start - 1 >= 0 and \
               mask[block.start - 1] == UNKNOWN:
                covering_blocks = self._covering_blocks(blocks_wo_this,
                                                        block.start)

                if 1 == max([block.length for block in covering_blocks]):
                    mask[block.start - 1] = WHITE

            # if the end of the block is BLACK and the next cell is UNKNOWN
            if mask[block.end] == BLACK and block.end + 1 < len(mask) and\
               mask[block.end + 1] == UNKNOWN:
                covering_blocks = self._covering_blocks(blocks_wo_this,
                                                        block.end)
                if 1 == max([block.length for block in covering_blocks]):
                    mask[block.end + 1] = WHITE

        logging.debug(debug_prefix + "{!s}".format(mask) + debug_suffix)

    def _covering_blocks(self, blocks, start, end=None):
        """Returns the blocks that includes the [start:end] portion."""
        if end is None:
            end = start

        return [block for block in blocks
                if block.start <= start and block.end >= end]
