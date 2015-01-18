#!/usr/bin/env python3

import os
import sys
import unittest

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from nonogram.raster import Raster
from nonogram.block import Block
from nonogram.column import Column
from nonogram.row import Row

from nonogram.raster import BLACK
from nonogram.raster import UNKNOWN
from nonogram.raster import WHITE


class TestSolver(unittest.TestCase):
    pass


if '__name__' == '__main__':
    unittest.main()
