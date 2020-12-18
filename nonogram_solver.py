#!/usr/bin/env python3.8
"""
A program that tries to solve nonograms.
"""

import argparse
import logging
import sys

from nonogram.raster import Raster
from nonogram import solver


def main(args=None):
    """
    Read the puzzle from the input file and start solving it.
    """
    logging.basicConfig(format='%(message)s',
                        level=logging.DEBUG if args.debug else logging.WARNING)
    with open(args.input_file, 'r') as inp:
        raster = Raster.from_file(inp)
        solution = solver.solve(raster)

        if not solution:
            print("Program couldn't find any solution.")
            logging.debug(str(raster))
            sys.exit(2)

        print(str(solution), end='')
        if args.bmp_file:
            solution.to_bitmap(args.bmp_file)


if __name__ == '__main__':
    # pylint: disable=invalid-name
    parser = argparse.ArgumentParser(description='Solve nonograms')
    parser.add_argument('input_file', help='file specifying the nonogram')
    parser.add_argument(
        '--bmp', dest='bmp_file', help='write the solution to the specified'
        ' file in BMP format')
    parser.add_argument('--debug', help='enable debug logs',
                        action='store_true')

    main(args=parser.parse_args())
