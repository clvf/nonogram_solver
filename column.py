"""
Class incorporating the information that we know of a column.
"""

import line

class Column(line.Line):

    def __init__(self, *args):
        super(Column, self).__init__(*args)
        self.is_row = False

    def __str__(self):
        str_ = "column: {!s}, ".format(not self.is_row)

        return str_ + super(Column, self).__str__()
