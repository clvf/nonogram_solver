"""
Implementation of the logic to solve the nonogram.
"""

import copy
import logging

from nonogram.rules import r1
from nonogram.rules import r2
from nonogram.rules import r3
from nonogram.solution import Solution
from nonogram import DiscrepancyInModel

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
            logging.debug("%s", raster)

        for meta in raster.col_meta:
            mask = raster.get_col(meta.idx)
            orig_meta = copy.deepcopy(meta)

            linesolve(mask, meta)

            if raster.update_col(mask=mask, idx=meta.idx) or meta != orig_meta:
                cells_changed = True
            logging.debug("%s", raster)

    if raster.is_solved():
        return Solution(raster.table)

    return None


def linesolve(mask, meta):
    """Rule based elimination on the received parameters."""
    for func in RULE_FUNCS:
        func(mask, meta)
        for block in meta.blocks:
            u = (block.end - block.start + 1) - block.length
            # assert u >= 0, "u: " + str(u) + " blk: " + str(block) + " meta: " + str(meta)
            # assert block.start >= 0, "block.start < 0, blk: " + str(block)
            # assert block.end < meta.size, "block ends outside of the boundary, blk: " + str(block)
            if u < 0:
                raise DiscrepancyInModel(
                    "u: " + str(u) + " blk: " + str(block) + " meta: " + str(meta)
                )

            if block.start < 0:
                raise DiscrepancyInModel("block.start < 0, meta: " + str(meta))

            if block.end >= meta.size:
                raise DiscrepancyInModel(
                    "block ends outside of the boundary, meta: " + str(meta)
                )


def bifurcate(raster):
    """Makes a guess, applies logical elimination and backtracks if discrepancy
    found."""
    for guess in raster.rank_guess_opts():
        _, idx, is_row = guess
        for guessed_raster in raster.make_guess(idx, is_row):
            try:
                solution = solve(guessed_raster)
            except DiscrepancyInModel as e:
                logging.debug("Discrepancy detected while bifurcating: %s", e)
                logging.debug("%s", guessed_raster)
                # this guess lead to a failure. try the next guess
                continue
            except:
                logging.error("%s", guessed_raster)
                raise

            # Logical elimination on the guessed raster didn't end in discrepancy.
            # Is the puzzl solved?
            if solution:
                return solution

            # not solved and no discrepancy found then branch further
            return bifurcate(guessed_raster)

    return None
