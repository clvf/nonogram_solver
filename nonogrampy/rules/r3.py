"""
Rules that refine ranges of blocks and color cells or let them empty.
"""

import logging

import nonogrampy
from nonogrampy import DiscrepancyInModel, rules
from nonogrampy.raster import BLACK
from nonogrampy.raster import WHITE


# pylint: disable=protected-access
@nonogrampy.log_changes("R3.1")
def fill_scattered_ranges(mask, meta):
    """Rule 3.1:

    Fill cells between first (m) and last (n) colored cell for a black
    run (j) and update range:

    rj.s = (m - u)
    rj.e = (n + u)
    where u = LBj - (n - m + 1)

    """
    for block in meta.blocks:
        runs = sorted(
            rules._runs_in_block_range(block, mask), key=lambda block: block.start
        )

        if not runs:
            continue

        (first, last) = (runs[0].start, runs[-1].end)

        blocks_wo_this = [blk for blk in meta.blocks if blk != block]

        # if the black run is covered only by the current block
        # ie. it is not covered by any of the other blocks...
        # TODO: check whether there's a covering block between (first,
        # last) not covering these two
        if (
            not rules._covering_blocks(blocks_wo_this, first)
            and not rules._covering_blocks(blocks_wo_this, last)
            and block.length >= (last - first + 1)
        ):
            # update mask
            if first < last:
                mask[first : last + 1] = [BLACK] * (last - first + 1)

            # len of the run
            runlen = block.length - (last - first + 1)

            # update the block's metadata
            if block.start < first - runlen:
                block.start = first - runlen

            if block.end > last + runlen:
                block.end = last + runlen


@nonogrampy.log_changes("R3.2")
def adjust_ranges_based_on_white_cells(mask, meta):
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
    logging.debug("R3.2: %s %s", mask, meta)

    non_white_runs = rules._get_non_white_runs(mask)

    logging.debug(
        "R3.2 non_white_runs: [%s]", "; ".join((str(block) for block in non_white_runs))
    )

    for block in meta.blocks:
        # iterate only over those runs that start or end within this block
        covered_runs = [
            r for r in non_white_runs if block.start <= r.end and block.end >= r.start
        ]
        logging.debug(
            "R3.2 block: %s, covered_runs: [%s]",
            block,
            "; ".join((str(block) for block in covered_runs)),
        )

        # Step 1.
        for run in covered_runs:
            # if the run starts outside of the boundaries of this block
            # but its "within boundary" length is long enough
            # then we cannot narrow further the start of the block
            if (
                run.start < block.start
                and rules._block_len_in_section(run, block) >= block.length
            ):
                break

            # Step 2.
            # if the block wouldn't fit in the run
            if rules._block_len_in_section(run, block) < block.length:
                continue
            else:
                logging.debug("R3.2 block.start = run.start: %s", block.start)
                block.start = run.start
                break

        # Step 3.
        for run in covered_runs[::-1]:
            # if the run ends outside of the boundaries of this block
            # but its "within boundary" length is long enough
            # then we cannot narrow further the end of the block
            if (
                block.end < run.end
                and rules._block_len_in_section(run, block) >= block.length
            ):
                break

            # Step 4.
            if rules._block_len_in_section(run, block) < block.length:
                continue
            else:
                logging.debug("R3.2 block.end = run.end: %s", block.end)
                block.end = run.end
                break

        # Step 5.
        blocks_wo_this = [blk for blk in meta.blocks if blk != block]

        # recompute covered_runs?

        for run in covered_runs:
            # if the non white run is covered only by the current block
            # (ie. it is not covered by any of the other blocks)
            # and is shorter than the block
            # then it can be marked as white
            # (non-white runs that are shorter than this one and not
            # covered by any other block should be set to white)
            if (
                # if run is entirely within the boundaries of this block
                block.start <= run.start
                and run.end <= block.end
                and not rules._covering_blocks(blocks_wo_this, run.start, run.end)
                and rules._block_len_in_section(run, block) < block.length
            ):
                logging.debug("R3.2 step 5: mark run as white: %s", run)
                for cell in mask[run.start : run.end + 1]:
                    # assert cell != BLACK, ("R3.2: segment contains black cell - '"
                    # + mask.decode("ascii") + "' '" + mask[run.start:run.end + 1].decode("ascii")
                    # + "', meta: " + str(meta))
                    if cell == BLACK:
                        raise DiscrepancyInModel(
                            "R3.2: segment contains black cell - "
                            "'{}' run: [{}:{}], meta: {}".format(
                                mask.decode("ascii"), run.start, run.end + 1, meta
                            )
                        )

                # update mask
                mask[run.start : run.end + 1] = [WHITE] * (run.end - run.start + 1)


def adjust_not_overlapping_black_runs(mask, meta):
    """Rule 3.3:
    This rule is designed for solving the situations that the range
    of black run j do not overlap the range of black run j − 1 or j + 1.
    """
    rule_3_3_1(mask, meta)
    rule_3_3_2(mask, meta)
    rule_3_3_3_1(mask, meta)
    rule_3_3_3_2(mask, meta)


@nonogrampy.log_changes("R3.3-1")
def rule_3_3_1(mask, meta):
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
        next_block = meta.blocks[idx + 1] if idx + 1 < len(meta.blocks) else None

        if mask[block.start] != BLACK:
            continue

        # if there's a previous block and it's overlapping then continue
        if prev_block and prev_block.end >= block.start:
            continue

        # either there's no previous block (this is the first block) or the
        # previous block range doesn't overlap with this one

        # (1) color this run's cells from "start"
        mask[block.start : block.start + block.length] = [BLACK] * block.length
        # and mark this run's boundaries as white
        if block.start > 0:  # if start -1 is within index range
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


@nonogrampy.log_changes("R3.3-2")
def rule_3_3_2(mask, meta):
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


@nonogrampy.log_changes("R3.3-3.1")
def rule_3_3_3_1(mask, meta):
    """Rule 3.3-3:

    For each black run j with its range not overlapping the range of black
    run j − 1, if there is more than one black segment in the range of the
    black run j, find out all black segments in (rjs, rje).
    Denote the number of these black segments to be b and index them as
    0, 1, ..., b − 1.

    (1) Set i = 0
    (2) Find the first black cell Cs in black segment i
    (3) Set m = i + 1
    (4) If m < b, find the first black cell Ct and the end black
        cell Ce in black segment m,

    If (e − s + 1) > LBj, stop and set rje = t − 2.
    Otherwise, m = m + 1 and go to step (4).
    """
    # pylint: disable=invalid-name
    for idx in range(len(meta.blocks)):
        prev_block = meta.blocks[idx - 1] if idx > 0 else None
        block = meta.blocks[idx]

        # if there's a previous block and it's overlapping then continue
        if prev_block and prev_block.end >= block.start:
            continue

        runs_in_range = rules._runs_starting_in_block_range(block, mask)
        for i in range(len(runs_in_range)):
            run_start = runs_in_range[i].start
            for m in range(i + 1, len(runs_in_range)):
                if runs_in_range[m].end - run_start + 1 > block.length:
                    block.end = runs_in_range[m].start - 2
                    break
            else:
                # continue as the inner loop wasn't broken
                continue
            # inner loop was broken, block's end has been updated
            break


@nonogrampy.log_changes("R3.3-3.2")
def rule_3_3_3_2(mask, meta):
    """Rule 3.3-3:

    For each black run j with its range not overlapping the range of black
    run j + 1, if there is more than one black segment in the range of the
    black run j, find out all black segments in (rjs, rje).
    Denote the number of these black segments to be b and index them as
    0, 1, ..., b − 1.

    (1) Set i = b - 1
    (2) Find the last black cell Ce in black segment i
    (3) Set m = i - 1
    (4) If m >= 0, find the last black cell Ct and the first black
        cell Cs in black segment m,

    If (e − s + 1) > LBj, stop and set rjs = t + 2.
    Otherwise, m = m - 1 and go to step (4).
    """
    # pylint: disable=invalid-name
    for idx in range(len(meta.blocks) - 1, -1, -1):
        prev_block = meta.blocks[idx + 1] if idx + 1 < len(meta.blocks) else None
        block = meta.blocks[idx]

        # if there's a previous block and it's overlapping then continue
        if prev_block and block.end >= prev_block.start:
            continue

        runs_in_range = rules._runs_ending_in_block_range(block, mask)
        for i in range(len(runs_in_range) - 1, -1, -1):
            run_end = runs_in_range[i].end
            for m in range(i - 1, -1, -1):
                if run_end - runs_in_range[m].start + 1 > block.length:
                    block.start = runs_in_range[m].end + 2
                    break
            else:
                # continue as the inner loop wasn't broken
                continue
            # inner loop was broken, block's start has been updated
            break


RULES = (
    fill_scattered_ranges,
    adjust_ranges_based_on_white_cells,
    adjust_not_overlapping_black_runs,
)

__all__ = ("RULES",)
