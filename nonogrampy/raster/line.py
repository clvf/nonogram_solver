"""
Class incorporating the meta information that we know of a row or column.
"""

import dataclasses
import typing


@dataclasses.dataclass
class Line:
    """
    Class incorporating the meta information that we know of a row or column.
    """

    # pylint: disable=too-few-public-methods
    size: int
    idx: int
    blocks: typing.List[typing.Any]
    nums: typing.Tuple[int, int]  # number of black & white cells according to the cues

    def __init__(self, size, idx, blocks):
        self.size = size
        self.idx = idx
        self.blocks = blocks

        nblack = 0
        for block in blocks:
            nblack += block.length

        self.nums = (nblack, size - nblack)

    def __str__(self):
        str_ = "{!s}, size: {!s}, blocks: [".format(self.idx, self.size)

        return str_ + "; ".join((str(block) for block in self.blocks)) + "]"


class Row(Line):
    """
    Class incorporating the information that we know of a row.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, *args):
        self.is_row = True
        super(Row, self).__init__(*args)

    def __str__(self):
        return "row: " + super(Row, self).__str__()


class Column(Line):
    """
    Class incorporating the information that we know of a column.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, *args):
        self.is_row = False
        super(Column, self).__init__(*args)

    def __str__(self):
        return "col: " + super(Column, self).__str__()
