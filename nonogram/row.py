"""
Class incorporating the information that we know of a row.
"""

from nonogram.line import Line


class Row(Line):
    def __init__(self, *args):
        self.is_row = True
        super(Row, self).__init__(*args)

    def __str__(self):
        return "row: " + super(Row, self).__str__()
