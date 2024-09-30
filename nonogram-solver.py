#!/usr/bin/env python3
"""
A program that tries to solve nonograms.
"""

import argparse
import logging
import sys

from nonogram.raster import Raster
from nonogram import solver


def repr_solution(solution, bmp_file):
    """Represent solution."""
    print(str(solution), end='')
    if bmp_file:
        solution.to_bitmap(bmp_file)


def main(args=None):
    """
    Read the puzzle from the input file and start solving it.
    """
    logging.basicConfig(format='%(message)s',
                        level=logging.DEBUG if args.debug else logging.INFO)
    with open(args.input_file, 'r') as inp:
        # TODO: this is ugly
        if args.format_nin:
            raster = Raster.from_nin_file(inp)
        else:
            raster = Raster.from_file(inp)

        solution = solver.solve(raster)

        if solution:
            repr_solution(solution, args.bmp_file)
            sys.exit(0)

        logging.debug("%s", raster)
        logging.info("No solution after pure logical elimination. Bifurcating...\n")

        if args.no_bifurcation:
            sys.exit(1)

        solution = solver.bifurcate(raster)

        if solution:
            repr_solution(solution, args.bmp_file)
            sys.exit(0)

        sys.exit(1)


if __name__ == '__main__':
    # pylint: disable=invalid-name
    parser = argparse.ArgumentParser(description='Solve nonograms')
    parser.add_argument('input_file', help='file specifying the nonogram')
    parser.add_argument(
        '--bmp', dest='bmp_file', help='write the solution to the specified'
        ' file in BMP format')
    parser.add_argument('--debug', help='enable debug logs',
                        action='store_true')
    parser.add_argument('--format-nin', help='input file has "NIN" format',
                        action='store_true')
    parser.add_argument('--no-bifurcation', help='Try to solve the puzzle only by logical elimination. Do not make guesses.',
                        action='store_true')

    main(args=parser.parse_args())
