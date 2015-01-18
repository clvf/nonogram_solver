"""
Class incorporating the information that we know of a row or column.
"""

from .commonequality import CommonEquality


class Line(CommonEquality):

    def __init__(self, size, idx, blocks):
        self.size = size
        self.idx = idx
        self.blocks = blocks

    def __str__(self):
        str_ = "idx: {!s}, size: {!s}, blocks: [".format(self.idx, self.size)

        return str_ + "; ".join((str(block) for block in self.blocks)) + "]"

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)