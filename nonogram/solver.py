"""
Implementation of the logic to solve the nonogram.
"""

import copy

from nonogram.rules import r1
from nonogram.rules import r2
from nonogram.rules import r3
from nonogram.solution import Solution

RULE_FUNCS = (*r1.RULES, *r2.RULES, *r3.RULES)


def solve(raster):
    """Does a rule based elimination on the raster object and returns a
    solution (object) if there's any and None otherwise."""
    cells_changed = True
    while cells_changed:
        cells_changed = False
        for meta in raster.row_meta:
            mask = raster.get_row(meta.idx)
            orig_meta = copy.deepcopy(meta)

            linesolve(mask, meta)

            if raster.update_row(mask=mask, idx=meta.idx) or meta != orig_meta:
                cells_changed = True

        for meta in raster.col_meta:
            mask = raster.get_col(meta.idx)
            orig_meta = copy.deepcopy(meta)

            linesolve(mask, meta)

            if raster.update_col(mask=mask, idx=meta.idx) or meta != orig_meta:
                cells_changed = True

    if raster.is_solved():
        return Solution(raster.table)

    return None


def linesolve(mask, meta):
    """Rule based elimination on the received parameters."""
    for func in RULE_FUNCS:
        func(mask, meta)
