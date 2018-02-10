"""
Class incorporating the meta information that we know of a row or column.
"""

from .commonequality import CommonEquality


class Line(CommonEquality):
    def __init__(self, size=None, idx=None, blocks=None):
        self.size = int(size)
        self.idx = int(idx)
        self.blocks = blocks

    def __str__(self):
        str_ = "{!s}, size: {!s}, blocks: [".format(self.idx, self.size)

        return str_ + "; ".join((str(block) for block in self.blocks)) + "]"
