"""
Implementation of the logic to solve the nonogram.
"""

import copy
import functools
import logging

from nonogram.block import Block
from nonogram.raster import BLACK
from nonogram.raster import UNKNOWN
from nonogram.raster import WHITE
from nonogram.solution import Solution


def log_changes(rule):
    """
    Decorator that logs the "trace" of the processing only if the wrapped
    function changed either the mask or the meta data.
    """

    def wrap(f):
        @functools.wraps(f)
        def wrapped_f(*args):
            mask = args[1]
            meta = args[2]
            orig_mask = copy.deepcopy(mask)
            orig_meta = copy.deepcopy(meta)
            f(*args)

            if mask != orig_mask:
                logging.debug(
                    "{} {}: {!s} -> {!s} {!s}".format(
                        rule, f.__name__, orig_mask, mask, meta
                    )
                )
            if meta != orig_meta:
                logging.debug(
                    "{} {}: {!s} -> {!s}".format(
                        rule, f.__name__, orig_meta, meta
                    )
                )

        return wrapped_f

    return wrap


class Solver(object):
    def solve(self, raster):
        """Does a rule based elimination on the raster object and returns a
        solution (object) if there's any and None otherwise."""
        logging.debug("\n=====\nRule Based Elimination:\n=====\n")
        cells_changed = True
        while (cells_changed):
            cells_changed = False
            for meta in raster.row_meta:
                mask = raster.get_row(meta.idx)
                orig_meta = copy.deepcopy(meta)

                self.linesolve(mask, meta)

                if raster.update_row(mask=mask, idx=meta.idx):
                    cells_changed = True

                if meta != orig_meta:
                    cells_changed = True

            for meta in raster.col_meta:
                mask = raster.get_col(meta.idx)
                orig_meta = copy.deepcopy(meta)

                self.linesolve(mask, meta)

                if raster.update_col(mask=mask, idx=meta.idx):
                    cells_changed = True

                if meta != orig_meta:
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

        # Rules 2.*
        self.check_meta_consistency(None, meta)
        self.look_for_trailing_white_cell(mask, meta)
        self.narrow_boundaries(mask, meta)

        # Rules 3.*
        self.fill_scattered_ranges(mask, meta)
        self.adjust_ranges_based_on_white_cells(mask, meta)
        self.adjust_not_overlapping_black_runs(mask, meta)

    @log_changes("R1.1")
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

        for block in meta.blocks:
            u = (block.end - block.start + 1) - block.length
            assert u >= 0, "u: " + str(u) + " blk: " + str(block)

            lb = block.start + u  # lower bound
            ub = block.end - u + 1  # upper bound
            if lb < ub:
                mask[lb:ub] = [BLACK] * (ub - lb)

    @log_changes("R1.2")
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
                for i in range(
                    meta.blocks[j].end + 1, meta.blocks[j + 1].start
                ):
                    mask[i] = WHITE

    @log_changes("R1.3")
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

        for idx in range(len(meta.blocks)):
            block = meta.blocks[idx]
            blocks_wo_this = [
                meta.blocks[i] for i in range(len(meta.blocks)) if idx != i
            ]

            # if the start of the block is BLACK and the preceding cell is
            # UNKNOWN
            if mask[block.start] == BLACK and block.start - 1 >= 0 and \
               mask[block.start - 1] == UNKNOWN:
                covering_blocks = self._covering_blocks(
                    blocks_wo_this, block.start
                )

                if covering_blocks and 1 == max(
                    [block.length for block in covering_blocks]
                ):
                    mask[block.start - 1] = WHITE

            # if the end of the block is BLACK and the next cell is UNKNOWN
            if mask[block.end] == BLACK and block.end + 1 < len(mask) and\
               mask[block.end + 1] == UNKNOWN:
                covering_blocks = self._covering_blocks(
                    blocks_wo_this, block.end
                )
                if covering_blocks and 1 == max(
                    [block.length for block in covering_blocks]
                ):
                    mask[block.end + 1] = WHITE

    def _covering_blocks(self, blocks, start, end=None):
        """Returns the blocks that includes the [start:end] portion."""
        if end is None:
            end = start

        return [
            block
            for block in blocks if block.start <= start and block.end >= end
        ]

    @log_changes("R1.4")
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

        black_runs = self._get_black_runs(mask)

        for i in range(len(black_runs) - 1):
            # if the two adjoint black run is separated by an UNKNOWN cell
            if black_runs[i + 1].start - black_runs[i].end == 1 and \
               mask[black_runs[i].end + 1] == UNKNOWN:
                covering_blocks = self._covering_blocks(
                    meta, black_runs[i].end, black_runs[i + 1].start
                )
                if covering_blocks:
                    covering_max_len = max(
                        [block.length for block in covering_blocks]
                    )
                    if covering_max_len < black_runs[i].length + \
                            black_runs[i + 1].length + 1:
                        mask[black_runs[i].end + 1] = WHITE

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

    @log_changes("R1.5")
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

        for i in range(1, len(mask) - 1):
            covering_blocks = self._covering_blocks(meta.blocks, i)
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
                    mask[lower_bound:upper_bound
                        ] = [BLACK] * (upper_bound - lower_bound)

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
                if (found_empty or
                    n == len(mask) - 1) and lower_bound < upper_bound:
                    mask[lower_bound:upper_bound
                        ] = [BLACK] * (upper_bound - lower_bound)

    @log_changes("R1.5")
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

        for block in self._get_black_runs(mask):
            covering_blocks = self._covering_blocks(
                meta.blocks, block.start, block.end
            )

            same_length = 1
            for cov in covering_blocks:
                if cov.length != block.length:
                    same_length = 0

            if same_length and covering_blocks:
                if block.start > 0:
                    mask[block.start - 1] = WHITE
                if block.end < len(mask) - 1:
                    mask[block.end + 1] = WHITE

    @log_changes("R2.1")
    def check_meta_consistency(self, mask, meta):
        """Rule 2.1:

        For each black run j, set
        rj.s = (r(j-1).s + LB(j-1) +1), if rj.s < r(j-1).s + LB(j-1) +1
        rj.e = (r(j+1).e - LB(j+1) -1), if rj.e > r(j+1).e - LB(j+1) -1
        """

        # check lower bound
        for j in range(len(meta.blocks) - 1):
            act = meta.blocks[j]
            next_ = meta.blocks[j + 1]
            earliest_start = act.start + act.length + 1
            if next_.start < earliest_start:
                next_.start = earliest_start

        # check upper bound
        for j in range(len(meta.blocks) - 2, -1, -1):
            act = meta.blocks[j]
            prev = meta.blocks[j + 1]
            latest_finish = prev.end - prev.length - 1
            if act.end > latest_finish:
                act.end = latest_finish

    @log_changes("R2.2")
    def look_for_trailing_white_cell(self, mask, meta):
        """Rule 2.2:

        rj.s = (rj.s + 1), if cell rj.s−1 is colored
        rj.e = (rj.e − 1), if cell rj.e+1 is colored
        """

        for j in range(len(meta.blocks)):
            block = meta.blocks[j]
            if block.start - 1 >= 0 and mask[block.start - 1] == BLACK:
                block.start += 1

            if block.end + 1 < len(mask) and mask[block.end + 1] == BLACK:
                block.end -= 1

    def _runs_in_block_range(self, block, mask):
        """Return the runs that are within the block range entirely."""
        return [
            run for run in self._get_black_runs(mask)
            if block.start <= run.start and run.end <= block.end
        ]

    def _is_segment_in_block_range(self, segment, blocks):
        """Return whether the segment is in the range of one of the blocks."""
        for block in blocks:
            if block.start <= segment.start and segment.end <= block.end:
                return True

        return False

    @log_changes("R2.3")
    def narrow_boundaries(self, mask, meta):
        """Rule 2.3:

        rj.s = (i.e + 2), if black segment i only belongs to the former black
                          runs of run j

        rj.e = (i.s − 2), if black segment i only belongs to the later black
                          runs of run j
        """
        for block_idx, block in enumerate(meta.blocks):

            runs_in_block_range = self._runs_in_block_range(block, mask)

            # runs in the block's range that are longer than the block length
            for black_segment in [
                r for r in runs_in_block_range if block.length < r.length
            ]:

                # if this is the last block in line
                if (
                    (
                        len(meta.blocks) == block_idx + 1
                        # or if black segment only belongs to the former black runs
                        or not self._is_segment_in_block_range(
                            black_segment, meta.blocks[block_idx + 1:]
                        )
                    )
                    # and it is worth the change
                    and block.start < black_segment.end + 2
                ):
                    block.start = black_segment.end + 2

                # if black segment only belongs to the later black runs
                if (
                    not self._is_segment_in_block_range(
                        black_segment, meta.blocks[:block_idx]
                    )
                    # and it is worth the change
                    and black_segment.start - 2 < block.end
                ):
                    block.end = black_segment.start - 2

    @log_changes("R3.1")
    def fill_scattered_ranges(self, mask, meta):
        """Rule 3.1:

        Fill cells between first (m) and last (n) colored cell for a black
        run (j) and update range:

        rj.s = (m - u)
        rj.e = (n + u)
        where u = LBj - (n - m + 1)

        """
        for block in meta.blocks:
            runs = sorted(
                self._runs_in_block_range(block, mask),
                key=lambda block: block.start
            )

            if len(runs) == 0:
                continue

            (first, last) = (runs[0].start, runs[-1].end)

            blocks_wo_this = [blk for blk in meta.blocks if blk != block]

            # if the black run is covered only by the current block
            # ie. it is not covered by any of the other blocks...
            # TODO: check whether there's a covering block between (first,
            # last) not covering these two
            if not self._covering_blocks(
                blocks_wo_this, first
            ) and not self._covering_blocks(
                blocks_wo_this, last
            ) and block.length >= (last - first + 1):
                # update mask
                if first < last:
                    mask[first:last + 1] = [BLACK] * (last - first + 1)

                # len of the run
                runlen = block.length - (last - first + 1)

                # update the block's metadata
                if block.start < first - runlen:
                    block.start = first - runlen

                if block.end > last + runlen:
                    block.end = last + runlen

    def _get_non_white_runs(self, mask):
        """Returns those runs that are delimeted by white cells."""
        res = []
        in_a_block = False
        last_idx = len(mask) - 1
        for idx, cell in enumerate(mask):
            if cell != WHITE and not in_a_block:
                in_a_block = True
                start = idx

            if cell == WHITE and in_a_block:
                in_a_block = False
                end = idx - 1
                res.append(Block(start, end, length=end - start + 1))

            if idx == last_idx and in_a_block:
                res.append(Block(start, last_idx, length=last_idx - start + 1))

        return res

    def _block_len_in_section(self, block, section):
        """Return the length of a block in a section [start, end]."""
        len_start = max(block.start, section.start)
        len_end = min(block.end, section.end)

        return len_end - len_start + 1


    @log_changes("R3.2")
    def adjust_ranges_based_on_white_cells(self, mask, meta):
        """Rule 3.2:

        For each black run j, find out all segments
        bounded by empty cells in (rjs , rje). Denote the number
        of these segments to be b and index them as 0, 1, ..., b − 1.

        Step 1. Set i = 0.

        Step 2. If the length of segment i is less than LBj, i = i + 1
        and go to step 2. Otherwise, set rjs = the start index
        of segment i, stop and go to step 3.

        Step 3. Set i = b − 1.

        Step 4. If the length of segment i is less than LBj, i = i − 1
        and go to step 4. Otherwise, set rje = the end index
        of segment i, stop and go to step 5.

        Step 5. If there still remain some segments with lengths less
        than LBj, for each of this kind of segments, if the
        segment does not belong to other black runs, all
        cells in this segment should be left empty.
        """
        # we're relying on that the non_white_runs contains the segments
        # sorted by start index
        logging.debug(
                    "{}: {!s} {!s}".format(
                        'R3.2', mask, meta
                    )
                )

        non_white_runs = self._get_non_white_runs(mask)

        logging.debug(
                    "{} non_white_runs: [{!s}".format(
                        'R3.2', "; ".join((str(block) for block in non_white_runs)) + "]"
                    )
                )

        for block in meta.blocks:
            # iterate only over those runs that are entirely contained by
            # the block
            contained_runs = [
                r for r in non_white_runs
                if block.start <= r.end and block.end >= r.start
            ]
            logging.debug(
                "{} block: {!s}, contained_runs: [{}]".format(
                            'R3.2', block, "; ".join((str(block) for block in contained_runs))
                        )
                    )

            for run in contained_runs:
                # if the run starts outside of the boundaries of this block
                # but its "within boundary" length is long enough
                # then we cannot narrow further the start of the block
                if run.start < block.start and self._block_len_in_section(run, block) >= block.length:
                    break

                # if the block wouldn't fit in the run
                if self._block_len_in_section(run, block) < block.length:
                    continue
                else:
                    logging.debug("R3.2 block.start: {}".format(str(block.start)))
                    block.start = run.start
                    logging.debug("R3.2 block.start = run.start: {}".format(str(block.start)))
                    break

            for run in contained_runs[::-1]:
                # if the run ends outside of the boundaries of this block
                # but its "within boundary" length is long enough
                # then we cannot narrow further the end of the block
                if block.end < run.end and self._block_len_in_section(run, block) >= block.length:
                    break

                if self._block_len_in_section(run, block) < block.length:
                    continue
                else:
                    logging.debug("R3.2 block.end: {}".format(str(block.end)))
                    block.end = run.end
                    logging.debug("R3.2 block.end = run.end: {}".format(str(block.end)))
                    break

            blocks_wo_this = [blk for blk in meta.blocks if blk != block]

            # recompute contained_runs?

            for run in contained_runs:
                # if the non white run is covered only by the current block
                # (ie. it is not covered by any of the other blocks)
                # and is shorter than the block
                # then it can be marked as white
                # (non-white runs that are shorter than this one and not
                # covered by any other block should be set to white)
                if not self._covering_blocks(
                    blocks_wo_this, run.start
                ) and not self._covering_blocks(
                    blocks_wo_this, run.end
                ) and self._block_len_in_section(run, block) < block.length:
                    for cell in mask[run.start:run.end + 1]:
                        assert cell != BLACK, "R3.2: non-white segment should not contain any black cell"

                    # update mask
                    mask[run.start:run.end + 1] = [WHITE] * (run.end - run.start + 1)


    def adjust_not_overlapping_black_runs(self, mask, meta):
        """Rule 3.3:
        This rule is designed for solving the situations that the range
        of black run j do not overlap the range of black run j − 1 or j + 1.
        """
        self.rule_3_3_1(mask, meta)
        self.rule_3_3_2(mask, meta)
        #rule_3_3_3()

    @log_changes("R3.3-1")
    def rule_3_3_1(self, mask, meta):
        """Rule 3.3-1:

        For each black run j with Crjs colored and its range not overlapping
        the range of black run j − 1,

        (1) Color cell Ci, where rjs + 1 ≤ i ≤ rjs + LBj − 1 and
            leave cell Crjs−1 and Crjs+LBi empty
        (2) Set rje = (rjs + LBj − 1)
        (3) If the range of black run j + 1 overlaps the range of
            black run j , set r(j+1)s = (rje + 2)
        (4) If r(j−1)e = rjs−1,r(j−1)e = rjs−2
        """
        for idx in range(len(meta.blocks)):
            prev_block = meta.blocks[idx - 1] if idx > 0 else None
            block = meta.blocks[idx]
            next_block = (
                meta.blocks[idx + 1] if idx + 1 < len(meta.blocks) else None
            )

            if mask[block.start] != BLACK:
                continue

            # if there's a previous block and it's overlapping then continue
            if prev_block and prev_block.end >= block.start:
                continue

            # either there's no previous block (this is the first block) or the
            # previous block range doesn't overlap with this one

            # (1) color this run's cells from "start"
            mask[block.start:block.start + block.length] = [BLACK] * block.length
            # and mark this run's boundaries as white
            if 0 < block.start:  # if start -1 is within index range
                mask[block.start - 1] = WHITE

            # if run end + 1 within index range
            if block.start + block.length < meta.size:
                mask[block.start + block.length] = WHITE

            # (2) adjust this run's end meta info
            block.end = block.start + block.length - 1
            # (4)
            if prev_block and prev_block.end == block.start - 1:
                assert block.start - 2 > 0
                prev_block.end = block.start - 2

            # (3)
            if next_block and next_block.start < block.end + 2:
                assert block.end + 2 < meta.size
                next_block.start = block.end + 2


    @log_changes("R3.3-2")
    def rule_3_3_2(self, mask, meta):
        """Rule 3.3-2:

        For each black run j with its range not overlapping the range of black
        run j − 1, if an empty cell cw appears after a black cell cb with cw
        and cb in the range of black run j . Set rje = w − 1
        """
        for idx in range(len(meta.blocks)):
            prev_block = meta.blocks[idx - 1] if idx > 0 else None
            block = meta.blocks[idx]

            # if there's a previous block and it's overlapping then continue
            if prev_block and prev_block.end >= block.start:
                continue

            first_black_cell_idx = meta.size
            for cell_idx in range(block.start, block.end + 1):
                if mask[cell_idx] == BLACK:
                    first_black_cell_idx = cell_idx
                    break

            first_white_cell_idx = -1
            for cell_idx in range(first_black_cell_idx, block.end + 1):
                if mask[cell_idx] == WHITE:
                    first_white_cell_idx = cell_idx
                    break

            if first_black_cell_idx < first_white_cell_idx:
                block.end = first_white_cell_idx - 1
