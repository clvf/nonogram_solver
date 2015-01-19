"""
Class representing the nonogram model.
"""

from functools import reduce
import copy

from .block import Block
from .column import Column
from .discrepancyinmodel import DiscrepancyInModel
from .row import Row

BLACK = 88   # \x58: ascii 'X'
UNKNOWN = 46  # \x2E: ascii '.'
WHITE = 32   # \x20: ascii ' '


class Raster(object):

    def __init__(self, **kwargs):
        self.table = kwargs['table']
        self.width = len(self.table[0])
        self.height = len(self.table)
        self.row_meta = kwargs['row_meta']
        self.col_meta = kwargs['col_meta']

    @staticmethod
    def parse_metadata(specification=None):
        header = specification.pop(0).split()
        (width, height) = (int(header[0]), int(header[1]))

        table = [bytearray((UNKNOWN for j in range(width)))
                 for i in range(height)]

        row_meta = list()
        col_meta = list()

        for idx in range(len(specification)):
            # it's a column if idx < width
            # and a row if idx >= width
            is_row = 0 if idx < width else 1
            size = height if not is_row else width
            meta_idx = idx if not is_row else idx - width

            blocks = [Block(0, size - 1, length)
                      for length in specification[idx].split()]

            if is_row:
                row_meta.append(Row(size, meta_idx, blocks))
            else:
                col_meta.append(Column(size, meta_idx, blocks))

        return dict(table=table, row_meta=row_meta, col_meta=col_meta)

    def __str__(self):
        repr_ = ""
        offset = "   "
        for i in range(self.width):
            line = offset + "|" * i
            line += "+" + "-" * (self.width - 1 - i) + " "
            line += "; ".join((str(block)
                              for block in self.col_meta[i].blocks))
            repr_ += line + "\n"

        header = offset
        for i in range(self.width):
            header += str(i % 10)
        repr_ += header + "\n"

        for i in range(self.height):
            line = " " + str(i % 10) + " "
            line += self.table[i].decode('ascii') + " "
            line += "; ".join((str(block)
                              for block in self.row_meta[i].blocks))
            repr_ += line + "\n"

        # repr_ = repr_ + "\n".join((str(meta) for meta in self.col_meta))
        # repr_ = repr_ + "\n" + "\n".join((str(meta) for meta in
        #                                   self.row_meta))

        return repr_ + "\n"

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
        (new, modified_cells) = self._update_list(rec=row, mask=mask)
        self._replace_row(row=new, idx=idx)

        return modified_cells

    def _replace_row(self, row=None, idx=None):
        """Replace the idx'th row of the internal table with the value in the
        params."""
        self.table[idx] = row

    def _update_list(self, rec=None, mask=None):
        """Updates the list based on the mask."""
        modified_cells = []
        original = copy.deepcopy(rec)

        for i in range(len(rec)):
            if rec[i] == UNKNOWN and mask[i] != UNKNOWN:
                rec[i] = mask[i]
                modified_cells.append(i)

            if rec[i] != UNKNOWN and mask[i] != UNKNOWN \
                    and rec[i] != mask[i]:
                raise DiscrepancyInModel(
                    "CURRENT: {!s} NEW: {!s}".format(original, mask))

        return rec, modified_cells

    def update_col(self, idx=None, mask=None):
        """Updates the UNKNOWN cells of the idx'th column based on the mask."""
        col = self.get_col(idx)
        (new, modified_cells) = self._update_list(rec=col, mask=mask)
        self._replace_col(col=new, idx=idx)

        return modified_cells

    def _replace_col(self, col=None, idx=None):
        """Replace the idx'th column of the internal table with the value in
        the params."""
        for cell_idx in range(len(col)):
            self.table[cell_idx][idx] = col[cell_idx]

#    def clone(self):
#        table_copy = copy.deepcopy(self.table)
#        row_meta_copy = [m.clone() for m in self.row_meta]
#        col_meta_copy = [m.clone() for m in self.col_meta]
#        return Raster(table=table_copy)
