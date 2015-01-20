"""
Class incorporating the information that we know of a column.
"""

from .line import Line


class Column(Line):

    def __init__(self, *args):
        self.is_row = False
        super(Column, self).__init__(*args)

    def __str__(self):
        return "column: " + super(Column, self).__str__()
