"""
Class incorporating the information that we have of a block.
"""

from .commonequality import CommonEquality


class Block(CommonEquality):

    def __init__(self, start, end, length):
        self.start = int(start)
        self.end = int(end)
        self.length = int(length)

    def __str__(self):
        str_ = "({!s}<->{!s}|len: {!s})".format(self.start, self.end,
                                                    self.length)
        return str_
