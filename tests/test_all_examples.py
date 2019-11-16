#!/usr/bin/env python3.8

import glob
import os
import sys
import unittest
import subprocess

SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
)
PROJ_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, os.path.pardir))
sys.path.append(PROJ_DIR)

class TestAll(unittest.TestCase):
    """Test the logic with all the files form the "examples" dir."""

    def test_all(self):
        """Test that there's no exception thrown for any of the riddles in the
        examples dir.
        Ie. test that by adding a new rule the model isn't corrupted.
        """
        for example in sorted(glob.glob(os.path.join(PROJ_DIR, 'examples', '*.txt'))):
            try:
                completed = subprocess.run(
                    [os.path.join(PROJ_DIR, 'nonogram_solver.py'), example],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print('OK: {}'.format(os.path.basename(example)))
            except subprocess.CalledProcessError as err:
                print('NOT OK: {}'.format(os.path.basename(example)))
                # if the solver couldn't find any solution at least it should
                # exit "gracefully" ie. with return code 2.
                self.assertEqual(err.returncode, 2)

if __name__ == '__main__':
    unittest.main()
