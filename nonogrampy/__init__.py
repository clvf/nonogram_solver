"""
The nonogrampy module.
"""

import copy
import functools
import logging

_LOGGER = logging.getLogger(__name__)


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
        """Wrapper"""

        @functools.wraps(func)
        def wrapped_f(mask, meta):
            """The new (wrapped) func"""
            if _LOGGER.isEnabledFor(logging.DEBUG):
                orig_mask = copy.deepcopy(mask)
                orig_meta = copy.deepcopy(meta)

            func(mask, meta)

            if _LOGGER.isEnabledFor(logging.DEBUG):
                if mask != orig_mask:
                    _LOGGER.debug(
                        "%s %s: %s -> %s %s", rule, func.__name__, orig_mask, mask, meta
                    )

                if meta != orig_meta:
                    _LOGGER.debug(
                        "%s %s: %s -> %s", rule, func.__name__, orig_meta, meta
                    )

        return wrapped_f

    return wrap
