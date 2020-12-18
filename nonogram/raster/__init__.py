"""
Module for the nonogram model.
"""

from functools import reduce
import copy
import os
import re

from nonogram import DiscrepancyInModel
from nonogram.raster import block
from nonogram.raster import line

BLACK = 88  # \x58: ascii 'X'
UNKNOWN = 46  # \x2E: ascii '.'
WHITE = 32  # \x20: ascii ' '

EMPTY = re.compile(r'^\s*$')
COMMENT = re.compile(r'^\s*#.*$')


def cleanse_puzzle(lines):
    """Delete emtpy lines and comments from the lines defining a puzzle"""
    return [
        line for line in lines
        if not re.match(EMPTY, line) and not re.match(COMMENT, line)
    ]


class Raster():
    """
    Class representing the nonogram model.
    """
    def __init__(self, table, row_meta, col_meta):
        self.table = table
        self.width = len(table[0])
        self.height = len(table)
        self.row_meta = row_meta
        self.col_meta = col_meta

    @classmethod
    def from_file(cls, file_):
        """Return a Raster object modelling the puzzle description passed in
        """
        file_content = cleanse_puzzle(file_.readlines())
        header = file_content.pop(0).split()
        (width, height) = (int(header[0]), int(header[1]))

        table = [
            bytearray((UNKNOWN for j in range(width))) for i in range(height)
        ]

        row_meta = list()
        col_meta = list()

        for idx in range(len(file_content)):
            # it's a column if idx < width
            # and a row if idx >= width
            is_row = 0 if idx < width else 1
            size = height if not is_row else width
            meta_idx = idx if not is_row else idx - width

            blocks = [
                block.Block(0, size - 1, int(length))
                for length in file_content[idx].split()
            ]

            if is_row:
                row_meta.append(line.Row(size, meta_idx, blocks))
            else:
                col_meta.append(line.Column(size, meta_idx, blocks))

        return cls(**dict(table=table, row_meta=row_meta, col_meta=col_meta))

    def __str__(self):
        repr_ = ""
        offset = "   "
        for i in range(self.width):
            line_ = offset + "|" * i
            line_ += "+" + "-" * (self.width - 1 - i) + " "
            line_ += "; ".join(
                (str(block) for block in self.col_meta[i].blocks))
            repr_ += line_ + os.linesep

        header = offset
        for i in range(self.width):
            header += str(i % 10)
        repr_ += header + os.linesep

        for i in range(self.height):
            line_ = " " + str(i % 10) + " "
            line_ += self.table[i].decode('ascii') + " "
            line_ += "; ".join(
                (str(block) for block in self.row_meta[i].blocks))
            repr_ += line_ + os.linesep

        return repr_ + os.linesep

    def get_row(self, idx):
        """Returns the copy of the idx'th row of the internal table."""
        return self.table[idx][:]

    def get_col(self, idx):
        """Returns the copy of the idx'th column of the internal table."""
        return bytearray((x[idx] for x in self.table))

    def is_solved(self):
        """If there's no "UNKNOWN" cell, then the puzzle is solved."""
        return reduce(lambda x, y: x and not UNKNOWN in y, self.table, True)

    def update_row(self, idx=None, mask=None):
        """Updates the UNKNOWN cells of the idx'th row based on the mask."""
        row = self.get_row(idx)
        (new, modified_cells) = self._update_list(rec=row, mask=mask, idx=idx,
                                                  type_='row')
        self._replace_row(row=new, idx=idx)

        return modified_cells

    def _replace_row(self, row=None, idx=None):
        """Replace the idx'th row of the internal table with the value in the
        params."""
        self.table[idx] = row

    def _update_list(self, rec=None, mask=None, idx=None, type_=None):
        """Updates the list based on the mask."""
        modified_cells = []
        original = copy.deepcopy(rec)

        for i in range(len(rec)):
            if rec[i] == UNKNOWN and mask[i] != UNKNOWN:
                rec[i] = mask[i]
                modified_cells.append(i)

            if (rec[i] != UNKNOWN and mask[i] != UNKNOWN
                    and rec[i] != mask[i]):
                raise DiscrepancyInModel(
                    "{}: {}, CURRENT: {!s} NEW: {!s}".format(
                        type_, str(idx), original, mask))

        return rec, modified_cells

    def update_col(self, idx=None, mask=None):
        """Updates the UNKNOWN cells of the idx'th column based on the mask."""
        col = self.get_col(idx)
        (new, modified_cells) = self._update_list(rec=col, mask=mask, idx=idx,
                                                  type_='col')
        self._replace_col(col=new, idx=idx)

        return modified_cells

    def _replace_col(self, col=None, idx=None):
        """Replace the idx'th column of the internal table with the value in
        the params."""
        for cell_idx in range(len(col)):
            self.table[cell_idx][idx] = col[cell_idx]
