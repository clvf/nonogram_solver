#!/usr/bin/env python

from glob import fnmatch
import os
import unittest

# pylint: disable=wrong-import-position
import nonogrampy
from nonogrampy import solver
from nonogrampy.raster import Raster

_PUZZLE_EXT = "nin"


class TestSolver(unittest.TestCase):
    def test_model_integrity(self):
        """Test that no discrepacy occurs during the solving process."""
        err_in_model = []
        for test_file in [
            os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "examples", f)
            for f in sorted(
                os.listdir(
                    os.path.join(
                        os.path.dirname(__file__), os.pardir, os.pardir, "examples"
                    )
                )
            )
            if fnmatch.fnmatch(f, f"*.{_PUZZLE_EXT}")
        ]:
            print(os.path.basename(test_file), end="")
            try:
                with open(test_file, "r") as fh:
                    if solver.solve(Raster.from_file(fh)):
                        print(": solved")
                    else:
                        print(": NOT solved")
            except nonogrampy.DiscrepancyInModel:
                err_in_model.append(test_file)

        self.assertFalse(err_in_model)


if __name__ == "__main__":
    unittest.main()
