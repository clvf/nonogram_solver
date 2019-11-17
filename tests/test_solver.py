#!/usr/bin/env python3.8

from glob import fnmatch
import os
import sys
import unittest

SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, os.path.pardir)))

# pylint: disable=wrong-import-position
import nonogram
from nonogram import solver
from nonogram.raster import Raster


class TestSolver(unittest.TestCase):
    def test_model_integrity(self):
        """Test that no discrepacy occurs during the solving process."""
        err_in_model = []
        for test_file in [
                os.path.join(
                    os.path.dirname(__file__), os.pardir, 'examples', f)
                for f in sorted(
                        os.listdir(
                            os.path.join(
                                os.path.dirname(__file__),
                                os.pardir,
                                'examples')))
                if fnmatch.fnmatch(f, '*.txt')
        ]:
            print(os.path.basename(test_file), end='')
            try:
                with open(test_file, 'rb') as fh:
                    if solver.solve(Raster.from_file(fh)):
                        print(': solved')
                    else:
                        print(': NOT solved')
            except nonogram.DiscrepancyInModel:
                err_in_model.append(test_file)

        self.assertFalse(err_in_model)


if __name__ == '__main__':
    unittest.main()
