"""
Class representing the nonogram modell.
"""

from functools import reduce
import copy

from .block import Block
from .column import Column
from .row import Row

BLACK = 88   # \x58: ascii 'X'
WHITE = 32   # \x20: ascii ' '
UNKNOWN = 46  # \x2E: ascii '.'


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
                row_meta.append(Row(size, idx, blocks))
            else:
                col_meta.append(Column(size, idx, blocks))

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

        return repr_ + "\n"

    def get_row_col(self, p_idx, p_is_row):
        """A metodus a belso tabla idx indexu soranak vagy oszlopanak
        _MASOLATAT_ adja vissza.
        """
        if p_is_row:
            res = self.table[p_idx][:]
        else:
            res = bytearray((x[p_idx] for x in self.table))

        return res

    def replace_row(self, p_idx, p_row):
        """A metodus lecsereli a belso tabla egy sorat a parameterben
        megadott sorral. Ez a metodus csak a melysegi bejaras alkalmaval
        kerul meghivasra."""
        self.table[p_idx] = p_row

    def is_solved(self):
        """If there's no "UNKNOWN" cell, then the puzzle is solved."""
        return reduce(lambda x, y: x and not UNKNOWN in y, self.table, True)

    def clone(self):
        table_copy = copy.deepcopy(self.table)
        # row_meta_copy = [m.clone() for m in self.row_meta]
        # col_meta_copy = [m.clone() for m in self.col_meta]
        return Raster(table=table_copy)
