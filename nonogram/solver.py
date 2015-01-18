"""
Implementation of the logic to solve the nonogram.
"""

from .solution import Solution


class DiscrepancyInModel(Exception):
    pass


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
        # return Solution(raster.table)
        return None

    def update(self, p_idx, p_is_row, p_mask):
        """A metodus a megadott maszk alapjan modositja a sor/oszlop
        maszktol eltero es meg nem kitoltott (UNKNOWN) mezoit.

        Ha volt valtoztatas, akkor a "modositasra merolegesen"
        frissiti a metaadatokat.
        """
        modified_cells = []  # a modositott cellak indexe
        cell_updated = 0  # tortent egyaltalan modositas?
        if p_is_row:
            # sor modositasa a mask alapjan
            for i in range(self.width):
                if self.table[p_idx][i] == UNKNOWN and p_mask[i] != UNKNOWN:
                    self.table[p_idx][i] = p_mask[i]
                    modified_cells.append(i)
                    cell_updated = 1
                if self.table[p_idx][i] != UNKNOWN and p_mask[i] != UNKNOWN \
                        and self.table[p_idx][i] != p_mask[i]:
                    raise DiscrepancyInModel("CURRENT: " + self.table[p_idx] + "\n"
                                             + "NEW:     " + str(p_mask))
            if cell_updated:
                if __debug__:
                    logging.debug("UPDATE: " + str(p_mask) + "\n")
                    logging.debug(self.debug_repr())
                # ezzel a modositassal teljesen ki van toltve a sor?
                self.change_made = 1
                # self.check_if_complete(self.row_metadata[p_idx])
        else:
            # az oszlop modositasa a mask alapjan
            for i in range(self.height):
                if self.table[i][p_idx] == UNKNOWN and p_mask[i] != UNKNOWN:
                    self.table[i][p_idx] = p_mask[i]
                    modified_cells.append(i)
                    cell_updated = 1
                if self.table[i][p_idx] != UNKNOWN and p_mask[i] != UNKNOWN \
                        and self.table[i][p_idx] != p_mask[i]:
                    raise DiscrepancyInModel("CURRENT: " + self.get_row_col(p_idx, p_is_row) + "\n"
                                             + "NEW:     " + str(p_mask))
            if cell_updated:
                if __debug__:
                    logging.debug("UPDATE: " + str(p_mask) + "\n")
                    logging.debug(self.debug_repr())
                self.change_made = 1
                # ezzel a modositassal teljesen ki van toltve az oszlop?
                # self.check_if_complete(self.col_metadata[p_idx])
