"""
The nonogram module.
"""

import copy
import functools
import logging


class DiscrepancyInModel(Exception):
    """
    Exception meaning that a discrepancy has been detected in the internal
    state of the model.
    """


def log_changes(rule):
    """
    Decorator that logs the "trace" of the processing only if the wrapped
    function changed either the mask or the meta data.
    """

    def wrap(func):
        @functools.wraps(func)
        def wrapped_f(mask, meta):
            orig_mask = copy.deepcopy(mask)
            orig_meta = copy.deepcopy(meta)
            func(mask, meta)

            if mask != orig_mask:
                logging.debug("{} {}: {!s} -> {!s} {!s}".format(
                    rule, func.__name__, orig_mask, mask, meta))
            if meta != orig_meta:
                logging.debug("{} {}: {!s} -> {!s}".format(
                    rule, func.__name__, orig_meta, meta))

        return wrapped_f

    return wrap
