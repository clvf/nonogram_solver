"""
Class representing the solution of a puzzle.
"""

import dataclasses
import logging
import struct
import typing

from nonogram import raster

# Globals
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BPP = 24


@dataclasses.dataclass
class Solution():
    """
    Class representing the solution of a puzzle.
    """
    table: typing.List[typing.List[int]]

    def __post_init__(self):
        self.width = len(self.table[0])
        self.height = len(self.table)

    def __str__(self):
        """String representation of the internal model."""
        return "\r\n".join(row.decode('ascii') for row in self.table) + "\r\n"

    def _compile_bmp_header(self):
        """
        Returns the BMP header.
        """
        return struct.pack(
            '<cc4IiiHH6I',
            'B',  # identifies the file type
            'M',  # identifies the file type
            0,  # size of the file
            0,  # application specific unused field
            54,  # offset: 14 + 40 (BMP header + DIB header)
            40,  # header size (BITMAPINFOHEADER)
            self.width,  # number of columns
            -1 * self.height,  # number of rows
            # (if <0 -> the picture won't be
            # upside down)
            1,  # number of color planes
            BPP,  # 24 bpp
            0,  # no compression
            0,  # size of the pixel array
            0,  # horisontal resolution
            0,  # vertical resolution
            0,  # number of colors in the palette
            0  # all colors are important
        )

    def _pack_bmp_pixels(self):
        """
        Returns the BMP representation of the solution.
        """
        color_depth = BPP / 8
        # number of padding bytes in a row:
        # (-1 * size of the pixels in bytes in the row) mod 4
        padbytes = (-1 * color_depth * self.width) % 4
        rowsize = self.width * color_depth + padbytes
        pixel_array = bytearray(255 for i in range(rowsize * self.height))
        y = 0
        for line in self.table.splitlines():
            for x in range(self.width):
                if line[x] == raster.BLACK:
                    start_idx = (y * rowsize) + x * color_depth
                    try:
                        pixel_array[start_idx:start_idx + color_depth] = BLACK
                    except IndexError as e:
                        logging.exception('BMP coordinates x,y: %d,%d; '
                                          'start idx: %d', x, y, start_idx)
                        raise e
            y += 1

        return pixel_array

    def to_bitmap(self, out_file):
        """
        Writes the BMP representation of the solution to the specified file.
        """
        with open(out_file, "wb") as bmp:
            bmp.write(self._compile_bmp_header())
            bmp.write(self._pack_bmp_pixels())
