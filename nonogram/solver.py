"""
Implementation of the logic to solve the nonogram.
"""

from .solution import Solution


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
