"""
Implementation of the logic to solve the nonogram.
"""

from .block import Block
from .raster import BLACK
from .raster import UNKNOWN
from .raster import WHITE
from .solution import Solution
import logging


class Solver(object):

    def solve(self, raster):
        """Does a rule based elimination on the raster object and returns a
        solution (object) if there's any and None otherwise."""
        logging.debug("\n=====\nRule Based Elimination:\n=====\n")
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
        self.mark_white_cell_bween_sgmts(mask, meta)
        self.fill_cells_based_on_boundary(mask, meta)
        self.mark_boundary_if_possible(mask, meta)

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

        debug_prefix = "R1.3 mark_white_cell_at_boundary: {!s} -> ".format(
            mask)
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

    def mark_white_cell_bween_sgmts(self, mask, meta):
        """Rule 1.4

        For any three consecutive cells ci-1, ci and ci+1, i = 1,...,n-2.
        Let max L be the maximal length of all black runs containing the three
        cells. Assumption: cells ci-1 and ci+1 are black, cell ci is unknown.
        If we color ci and find that the length of the new black segment
        containing ci is larger than max L, ci should be left empty.
        """
        # return if this line already "solved" completely
        if UNKNOWN not in mask:
            return

        debug_prefix = "R1.4 mark_white_cell_bween_sgmts: {!s} -> ".format(
            mask)
        debug_suffix = ", {!s}".format(meta)

        black_runs = self._get_black_runs(mask)

        for i in range(len(black_runs) - 1):
            # if the two adjoint black run is separated by an UNKNOWN cell
            if black_runs[i + 1].start - black_runs[i].end == 1 and \
               mask[black_runs[i].end + 1] == UNKNOWN:
                covering_blocks = self._covering_blocks(meta,
                                                        black_runs[i].end,
                                                        black_runs[i + 1].start)
                if covering_blocks:
                    covering_max_len = max(
                        [block.length for block in covering_blocks])
                    if covering_max_len < black_runs[i].length + \
                            black_runs[i + 1].length + 1:
                        mask[black_runs[i].end + 1] = WHITE

        logging.debug(debug_prefix + "{!s}".format(mask) + debug_suffix)

    def _get_black_runs(self, mask):
        """Returns those runs start and end indices that don't contain any
        WHITE or UNKNOWN cell."""
        res = []
        size = len(mask)
        start = 0
        while start < size:
            # if we found a black cell
            if mask[start] == BLACK:
                end = size - 1

                # look ahead if we find a black cell or reach the end
                for idx in range(start, size):
                    if mask[idx] != BLACK:
                        end = idx - 1
                        break

                res.append(Block(start, end, length=end - start + 1))

                start = end + 1
            else:
                start += 1

        return res

    def fill_cells_based_on_boundary(self, mask, meta):
        """Rule 1.5

        For any two consecutive cells ci-1 and ci, i = 1,...,n-1. Constraint:
        cell ci-1 must be empty or unknown and cell ci must be black.
        (1) Let minL be the minimal length of all black runs covering ci.
        (2) Find an empty cell cm closest to ci, i-minL+1 <= m <= i-1. If cm
        exists, color each cell cp where i+1 <= p <= m+minL
        (3) Find an empty cell cn closest to ci, i+1 <= n <= i+minL-1. If cn
        exists, color each cell cp where n-minL <= p <= i-1
        """
        # return if this line already "solved" completely
        if UNKNOWN not in mask:
            return

        debug_prefix = "R1.5 fill_cells_based_on_boundary: {!s} -> ".format(
            mask)
        debug_suffix = ", {!s}".format(meta)

        for i in range(1, len(mask) - 1):
            covering_blocks = self._covering_blocks(meta.blocks, i)
            minL = min([block.length for block in covering_blocks])

            found_empty = 0
            m, n = -1, -1
            if minL > 0 and mask[i - 1] != BLACK and mask[i] == BLACK:
                # search for an emtpy cell "to the left" from ci
                for m in range(i - 1, max(i - minL, -1), -1):
                    if mask[m] == WHITE:
                        found_empty = 1
                        break

                lower_bound = i + 1
                upper_bound = m + minL + 1 if found_empty else minL

                # if an empty cell is found or we reached the wall and the
                # lower bound is less than the upper bound
                if (found_empty or m == 0) and lower_bound < upper_bound:
                    mask[lower_bound:upper_bound] = [
                        BLACK] * (upper_bound - lower_bound)

            found_empty = 0
            if minL > 0 and mask[i + 1] != BLACK and mask[i] == BLACK:
                # search for an emtpy cell "to the right" from ci
                for n in range(i + 1, min(i + minL, len(mask))):
                    if mask[n] == WHITE:
                        found_empty = 1
                        break

                lower_bound = n - minL if found_empty else len(mask) - minL
                upper_bound = i

                # if an empty cell is found or we reached the wall and the
                # lower bound is less than the upper bound
                if (found_empty or n == len(mask) - 1) and lower_bound < upper_bound:
                    mask[lower_bound:upper_bound] = [
                        BLACK] * (upper_bound - lower_bound)

        logging.debug(debug_prefix + "{!s}".format(mask) + debug_suffix)

    def mark_boundary_if_possible(self, mask, meta):
        """Rule 1.5:

        If all black runs covering ci have the same length as that of the
        block segment containing ci.
        (1) Let s and e be the start and end indices of the black segment
            containing ci
        (2) Leave cells c.s-1 and c.e+1 empty
        """
        # return if this line already "solved" completely
        if UNKNOWN not in mask:
            return

        debug_prefix = "R1.5 mark_boundary_if_possible: {!s} -> ".format(mask)
        debug_suffix = ", {!s}".format(meta)

        for block in self._get_black_runs(mask):
            covering_blocks = self._covering_blocks(
                meta.blocks, block.start, block.end)

            same_length = 1
            for cov in covering_blocks:
                if cov.length != block.length:
                    same_length = 0

            if same_length and len(covering_blocks) > 0:
                if block.start > 0:
                    mask[block.start - 1] = WHITE
                if block.end < len(mask) - 1:
                    mask[block.end + 1] = WHITE

        logging.debug(debug_prefix + "{!s}".format(mask) + debug_suffix)
