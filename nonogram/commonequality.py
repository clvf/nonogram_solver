"""
Class implementing a common equality method.
"""


class CommonEquality(object):
    def __eq__(self, other):
        return (
            isinstance(other, type(self)) and self.__dict__ == other.__dict__
        )

    def __ne__(self, other):
        return not self.__eq__(other)
