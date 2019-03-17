"""
Offers a few functions that could help while debugging.

:author: Jonathan Decker

This decorators can be used to debug functions.
In order to use them import this module and add @functionname
on top of the function def you wish to debug.
For example:

@timer
def do_something(value):
    # do work
    return

"""
import logging
import functools
import time

logger = logging.getLogger('scrap_logger')


def timer(func):
    """
    Wrapper that records the execution time and logs it.
    :param func: function
    :return: wrapper_timer
    """

    # log the runtime of the decorated function
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        logger.debug(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer


def debug(func):
    """
    Wrapper that logs the called function, the given arguments and the returned value.
    :param func: function
    :return: wrapper_debug
    """

    # log the function signature and return value
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        logger.debug(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        logger.debug(f"{func.__name__!r} returned {value!r}")
        return value
    return wrapper_debug
