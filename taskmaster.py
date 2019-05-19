"""
Handles calls from the discord_bot.
This module takes calls with arguments, finds the correct functions
and starts them via a multithreaded worker pool.
:author: Jonathan Decker
"""
from typing import List
import logging
from utils.lookup_tables import call_list, time_frame_list, filter_list, time_frame_lookup, filter_lookup, scrape_lookup
from utils.task_queue import SingleTask, TaskGroup, submit_task_group
from utils.lookup_tables import scrape_task_lookup, stalk_task_lookup

logger = logging.getLogger('scrap_logger')


class UnknownArgumentError(Exception):
    """
    Raised when for a given argument no matching call or filter can be found
    """
    pass


def call_taskmaster(args: List[str], is_scrape: bool):
    """
    Main function of this module, takes a list of arguments and returns the scraped TournamentList
    :param args: List[str], the args must be valid according to the lookups in this module
    :param is_scrape: bool, tells if this was called as part of a scrape or stalk command
    :return: TournamentList, containing all tournaments returned for the given command
    """

    # call interpret_args to find the fitting tasks
    calls, filters, time_frame = interpret_args(args, is_scrape)
    logger.debug(
        "Interpreted args as calls: " + str(calls) + "\nand filters: " + str(filters) + "\nand time_frame: " + str(
            time_frame))

    # check for invalid amount of calls
    if len(calls) == 0:
        logger.debug("No viable calls in command, stopping...")
        return "No viable calls in command."
    if len(time_frame) > 1:
        logger.debug("Only one the first time_frame will be used")
    real_time_frame = time_frame[0]

    # create the SingleTask objects
    tasks = []
    for call in calls:
        task = create_single_task(call, is_scrape, real_time_frame)
        tasks.append(task)

    # create TaskGroup
    task_group = TaskGroup(tasks, "calls: " + str(calls))

    # submit TaskGroup to multiprocessing
    logger.debug("Submitting TaskGroup with " + str(task_group.task_count) + " tasks")
    results = submit_task_group(task_group)

    # merge results into a single TournamentList
    total_tl = results.pop()
    for tl in results:
        total_tl.merge_tournament_lists(tl)

    # remove duplicates from the combines results
    total_tl.remove_duplicates()

    # apply filter to results
    logger.debug("Applying filters to " + str(len(total_tl)) + " tournaments")
    for filter_ in filters:
        total_tl = total_tl.filter_format(filter_)

    # return results to discord_bot
    logger.debug("Results are ready, " + str(len(total_tl)) + " tournaments remain")
    return str(total_tl)


def aliases_lookup(arg: str, is_scrape: bool):
    """
    Takes an alias and returns the full argument
    :param arg: str, a valid alias for the real argument
    :param is_scrape: bool, tells if this was called as part of a scrape or stalk command
    :return: str, the real arg name
    """
    # turn arg to lowercase and merge lookup dict
    lower_arg = arg.lower()
    if is_scrape:
        lookup = {**scrape_lookup, **filter_lookup}
    else:
        lookup = {**filter_lookup, **filter_lookup}

    lookup = {**lookup, **time_frame_lookup}

    # use dict to find concrete arg
    real_arg = lookup.get(lower_arg, "unknown")
    if real_arg is "unknown":
        logger.warning("Unkwon argument found: " + arg)
        raise UnknownArgumentError

    # return the concrete arg or throw an unknown arg exception
    return real_arg


def split_calls_time_frame_filter(args: List[str]):
    """
    Splits a given list of arguments in calls, filters and time_frames
    :param args: List[str], all str must be valid real args, no aliases
    :return: (List[str], List[str], List[str]), a tuple containing calls, filters, time_frames
    """
    # split args into calls, filter and time_frame, also filters out unknown args
    calls = []
    filter_ = []
    time_frame = []
    for arg in args:
        if arg in call_list:
            calls.append(arg)
        if arg in filter_list:
            filter_.append(arg)
        if arg in time_frame_list:
            time_frame.append(arg)

    # return tuple
    return calls, filter_, time_frame


def interpret_args(args: List[str], is_scrape: bool):
    """
    Takes a list of args and returns a tuple without aliases split into calls, filters, time_frames
    :param args: List[str], containing any valid args
    :param is_scrape: bool, tells if this is part of scrape or stalk command
    :return: (List[str], List[str], List[str]), tuple containing calls, filters, time_frames
    """
    # use lookup table to understand aliases
    no_aliases = []
    for arg in args:
        try:
            no_aliases.append(aliases_lookup(arg, is_scrape))
        except UnknownArgumentError:
            logger.error("Can't understand a given argument: " + arg)
            pass

    # split calls and filter
    calls, filter_, time_frame = split_calls_time_frame_filter(no_aliases)

    # return tuple with args for calls and filter
    return calls, filter_, time_frame


def create_single_task(call, is_scrape, *args):
    """
    Creates a Single Task object using the lookup tables to find the correct function.
    :param call: str, will be checked against the task_lookup tables in lookup_tables
    :param is_scrape: bool, determines in what table to look
    :param args: tuple(any), arguments for the call
    :return: SingleTask, with the function associated to the call and the args as args
    """
    # use lookup to find scraper responsible for task
    if is_scrape:
        task = scrape_task_lookup.get(call)
    else:
        task = stalk_task_lookup.get(call)
    return SingleTask(task, *args)
