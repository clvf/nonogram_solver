"""
Rules to refine the ranges of the blocks.
"""
import nonogram
from nonogram import rules
from nonogram.raster import BLACK


# pylint: disable=protected-access
@nonogram.log_changes("R2.1")
def check_meta_consistency(_, meta):
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


@nonogram.log_changes("R2.2")
def look_for_trailing_white_cell(mask, meta):
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


@nonogram.log_changes("R2.3")
def narrow_boundaries(mask, meta):
    """Rule 2.3:

    rj.s = (i.e + 2), if black segment i only belongs to the former black
                        runs of run j

    rj.e = (i.s − 2), if black segment i only belongs to the later black
                        runs of run j
    """
    for block_idx, block in enumerate(meta.blocks):

        runs_in_block_range = rules._runs_in_block_range(block, mask)

        # runs in the block's range that are longer than the block length
        for black_segment in [
                r for r in runs_in_block_range if block.length < r.length
        ]:

            # if this is the last block in line
            if ((
                    len(meta.blocks) == block_idx + 1
                    # or if black segment only belongs to the former black runs
                    or not rules._is_segment_in_block_range(
                        black_segment, meta.blocks[block_idx + 1:]))
                    # and it is worth the change
                    and block.start < black_segment.end + 2):
                block.start = black_segment.end + 2

            # if black segment only belongs to the later black runs
            if (not rules._is_segment_in_block_range(black_segment,
                                                     meta.blocks[:block_idx])
                    # and it is worth the change
                    and black_segment.start - 2 < block.end):
                block.end = black_segment.start - 2
