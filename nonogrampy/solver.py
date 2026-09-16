"""
Implementation of the logic to solve the nonogram.
"""

import copy
import logging
import sys

from nonogrampy import rules as r
from nonogrampy.rules import r1
from nonogrampy.rules import r2
from nonogrampy.rules import r3
from nonogrampy.solution import Solution
from nonogrampy import DiscrepancyInModel
from nonogrampy import raster as rstr

RULE_FUNCS = (*r1.RULES, *r2.RULES, *r3.RULES)


def linesolve(raster):
    """Does a rule based elimination on the raster object and returns a
    solution (object) if there's any and None otherwise."""
    cells_changed = True
    while cells_changed:
        cells_changed = False
        for meta in raster.row_meta:
            mask = raster.get_row(meta.idx)
            orig_meta = copy.deepcopy(meta)

            linesolve_inner(mask, meta)

            if raster.update_row(mask=mask, idx=meta.idx) or meta != orig_meta:
                cells_changed = True
            logging.debug("%s", raster)

        for meta in raster.col_meta:
            mask = raster.get_col(meta.idx)
            orig_meta = copy.deepcopy(meta)

            linesolve_inner(mask, meta)

            if raster.update_col(mask=mask, idx=meta.idx) or meta != orig_meta:
                cells_changed = True
            logging.debug("%s", raster)

    if raster.is_solved():
        return Solution(raster.table)

    return None


def linesolve_inner(mask, meta):
    """Rule based elimination on the received parameters."""
    for rule in RULE_FUNCS:
        rule(mask, meta)
        validate(mask, meta)


def validate(mask, meta):
    """Check for discrepancies between the metadata and the actual "coloring"."""
    nblack, nwhite = meta.nums

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

    cblack, cwhite = rstr.filled_cnt(mask)
    # if more cells are colored to black or white than it should...
    if cblack > nblack or cwhite > nwhite:
        raise DiscrepancyInModel(
            "nblack: {}, actually colored: {}, nwhite: {}, actually colored {}, meta: {}".format(
                nblack, cblack, nwhite, cwhite, meta
            )
        )

    # if the line is "solved" (although UNKNOWN cells can still appear)
    if cblack == nblack:
        black_runs = r._get_black_runs(mask)
        # then there should be exactly as many black runs as the meta says
        if len(black_runs) != len([b for b in meta.blocks if b.length > 0]):
            raise DiscrepancyInModel(
                "len(black_runs) != len(meta.blocks):  {} != {} mask: '{}', meta: {}".format(
                    len(black_runs), len(meta.blocks), mask.decode("ascii"), meta
                )
            )


def bifurcate(raster):
    """Makes a guess, applies logical elimination and backtracks if discrepancy
    found."""

    row_idx = raster.find_row_with_unknown()

    guessed_raster = raster.guess_black(row_idx)
    solution = bifurcate_inner(guessed_raster)

    if solution:
        return solution

    # not solved
    guessed_raster = raster.guess_white(row_idx)
    solution = bifurcate_inner(guessed_raster)

    if solution:
        return solution

    return None


def bifurcate_inner(guessed_raster, print_raster=False):
    try:
        solution = linesolve(guessed_raster)
    except DiscrepancyInModel as e:
        logging.debug("Discrepancy detected while bifurcating: %s", e)
        logging.debug("%s", guessed_raster)
        return None
    except:
        logging.error("%s", guessed_raster)
        raise

    if solution:
        return solution

    # not solved:
    return bifurcate(guessed_raster)


def solve(raster, no_bifurcation=False):
    """Performs logical elimination and continues with bifurcation if needed.  Returns
    a solution (object) if there's any and None otherwise."""
    solution = linesolve(raster)

    if solution:
        return solution

    if no_bifurcation:
        logging.info("%s", raster)
        sys.exit(1)

    logging.info("No solution after pure logical elimination. Bifurcating...\n")
    return bifurcate(raster)
