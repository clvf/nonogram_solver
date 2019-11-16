"""
Module containing the rules that are used to solve the puzzle with logical
elimination.
"""
from nonogram.raster import BLACK
from nonogram.raster import UNKNOWN
from nonogram.raster import WHITE
from nonogram.raster.block import Block
from nonogram.rules import r1
from nonogram.rules import r2
from nonogram.rules import r3

R1_RULES = (r1.fill_intersections, r1.check_spaces,
            r1.mark_white_cell_at_boundary, r1.mark_white_cell_bween_sgmts,
            r1.fill_cells_based_on_boundary, r1.mark_boundary_if_possible)

R2_RULES = (r2.check_meta_consistency, r2.look_for_trailing_white_cell,
            r2.narrow_boundaries)

R3_RULES = (r3.fill_scattered_ranges, r3.adjust_ranges_based_on_white_cells,
            r3.adjust_not_overlapping_black_runs)

RULE_FUNCS = (*R1_RULES, *R2_RULES, *R3_RULES)


def _covering_blocks(blocks, start, end=None):
    """Returns the blocks that includes the [start:end] portion."""
    if end is None:
        end = start

    return [
        block for block in blocks if block.start <= start and block.end >= end
    ]


def _get_black_runs(mask):
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


def _runs_in_block_range(block, mask):
    """Return the runs that are within the block range entirely."""
    return [
        run for run in _get_black_runs(mask)
        if block.start <= run.start and run.end <= block.end
    ]


def _is_segment_in_block_range(segment, blocks):
    """Return whether the segment is in the range of one of the blocks."""
    for block in blocks:
        if block.start <= segment.start and segment.end <= block.end:
            return True

    return False


def _get_non_white_runs(mask):
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


def _block_len_in_section(block, section):
    """Return the length of a block in a section [start, end]."""
    len_start = max(block.start, section.start)
    len_end = min(block.end, section.end)

    return len_end - len_start + 1


def _runs_starting_in_block_range(block, mask):
    """Return the runs that start within the block range and may end
    outside."""
    return [
        run for run in _get_black_runs(mask)
        if block.start <= run.start and run.start <= block.end
    ]


def _runs_ending_in_block_range(block, mask):
    """Return the runs that end within the block range and may start before
    """
    return [
        run for run in _get_black_runs(mask)
        if block.start <= run.end and run.end <= block.end
    ]


__all__ = ('RULE_FUNCS', )
