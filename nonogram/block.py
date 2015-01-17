"""
Class incorporating the information that we have of a block.
"""


class Block(object):

    def __init__(self, start, end, length):
        self.start = start
        self.end = end
        self.length = length

    def __str__(self):
        str_ = "s: {!s}, e: {!s}, len: {!s}".format(self.start, self.end,
                                                    self.length)
        return str_
