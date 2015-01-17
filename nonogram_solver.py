#!/usr/bin/env python3

from nonogram.raster import Raster
from nonogram.solver import Solver
import argparse
import logging
import sys


def initialize_raster(file_content):
    """Process the file_content and returns a Raster object."""
    raster_internals = Raster.parse_metadata(specification=file_content)
    return Raster(**raster_internals)


def main(args=None):
    # logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    with open(args.input_file, 'r') as INPUT:
        raster = initialize_raster(INPUT.readlines())
        logging.info("\n=====\nRule Based Elimination:\n=====\n")
        solution = Solver().solve(raster)

        if not solution:
            print("Program couldn't find any solution.")
            logging.info(str(raster))
            sys.exit(1)

        print(str(solution), end='')
        if args.bmp_file:
            # solution.to_bitmap(args.bmp_file)
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Solve nonograms')
    parser.add_argument('input_file', help='file specifying the nonogram')
    parser.add_argument('--bmp-file', dest='bmp_file',
                        help='write the solution to the specified file in BMP format')

    main(args=parser.parse_args())
