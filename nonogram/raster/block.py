"""
Class incorporating the information that we have of a block.
"""

import dataclasses


@dataclasses.dataclass
class Block():
    """
    Class incorporating the information that we have of a block.
    """

    start: int
    end: int
    length: int

    def __str__(self):
        return "({!s}<->{!s}|len: {!s})".format(self.start, self.end,
                                                self.length)
