"""
Rules to determinde which cells to be colored or left empty.
"""

import nonogram
from nonogram import DiscrepancyInModel, rules
from nonogram.raster import BLACK
from nonogram.raster import UNKNOWN
from nonogram.raster import WHITE


# pylint: disable=protected-access
@nonogram.log_changes("R1.1")
def fill_intersections(mask, meta):
    """Rule 1.1:

    for each black run j, cell ci will be colored when
    rj.s+u <= i <= rj.e - u
    where u = (rj.e - rj.s + 1) -LBj
    and LBj is the length of a black run j
    """
    # return if this line already "solved" completely
    if UNKNOWN not in mask:
        return

    # pylint: disable=invalid-name
    for block in meta.blocks:
        u = (block.end - block.start + 1) - block.length
        #assert u >= 0, "u: " + str(u) + " blk: " + str(block) + " meta: " + str(meta)

        lb = block.start + u  # lower bound
        ub = block.end - u + 1  # upper bound
        if lb < ub:
            mask[lb:ub] = [BLACK] * (ub - lb)


@nonogram.log_changes("R1.2")
def check_spaces(mask, meta):
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

    # if there are no black runs in the row/col at all...
    if not meta.blocks or meta.blocks[0].length == 0:
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


@nonogram.log_changes("R1.3")
def mark_white_cell_at_boundary(mask, meta):
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

    for idx in range(len(meta.blocks)):
        block = meta.blocks[idx]
        blocks_wo_this = [
            meta.blocks[i] for i in range(len(meta.blocks)) if idx != i
        ]

        # if the start of the block is BLACK and the preceding cell is
        # UNKNOWN
        if (mask[block.start] == BLACK and block.start - 1 >= 0
                and mask[block.start - 1] == UNKNOWN):
            covering_blocks = rules._covering_blocks(blocks_wo_this,
                                                     block.start)

            if (covering_blocks
                    and max([block.length for block in covering_blocks]) == 1):
                mask[block.start - 1] = WHITE

        # if the end of the block is BLACK and the next cell is UNKNOWN
        if (mask[block.end] == BLACK and block.end + 1 < len(mask)
                and mask[block.end + 1] == UNKNOWN):
            covering_blocks = rules._covering_blocks(blocks_wo_this, block.end)
            if (covering_blocks
                    and max([block.length for block in covering_blocks]) == 1):
                mask[block.end + 1] = WHITE


@nonogram.log_changes("R1.4")
def mark_white_cell_bween_sgmts(mask, meta):
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

    black_runs = rules._get_black_runs(mask)

    for i in range(len(black_runs) - 1):
        # if the two adjoint black run is separated by an UNKNOWN cell
        if (black_runs[i + 1].start - black_runs[i].end == 1
                and mask[black_runs[i].end + 1] == UNKNOWN):
            covering_blocks = rules._covering_blocks(meta, black_runs[i].end,
                                                     black_runs[i + 1].start)
            if covering_blocks:
                covering_max_len = max(
                    [block.length for block in covering_blocks])
                if (covering_max_len <
                        black_runs[i].length + black_runs[i + 1].length + 1):
                    mask[black_runs[i].end + 1] = WHITE


@nonogram.log_changes("R1.5")
def fill_cells_based_on_boundary(mask, meta):
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

    # pylint: disable=invalid-name
    for i in range(1, len(mask) - 1):
        covering_blocks = rules._covering_blocks(meta.blocks, i)
        minL = 0
        if covering_blocks:
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
                mask[lower_bound:upper_bound] = [BLACK] * (upper_bound -
                                                           lower_bound)

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
            if (found_empty
                    or n == len(mask) - 1) and lower_bound < upper_bound:
                mask[lower_bound:upper_bound] = [BLACK] * (upper_bound -
                                                           lower_bound)


@nonogram.log_changes("R1.5")
def mark_boundary_if_possible(mask, meta):
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

    for block in rules._get_black_runs(mask):
        covering_blocks = rules._covering_blocks(meta.blocks, block.start,
                                                 block.end)

        same_length = 1
        for cov in covering_blocks:
            if cov.length != block.length:
                same_length = 0

        if same_length and covering_blocks:
            if block.start > 0:
                mask[block.start - 1] = WHITE
            if block.end < len(mask) - 1:
                mask[block.end + 1] = WHITE


RULES = (fill_intersections, check_spaces, mark_white_cell_at_boundary,
         mark_white_cell_bween_sgmts, fill_cells_based_on_boundary,
         mark_boundary_if_possible)

__all__ = ('RULES', )
