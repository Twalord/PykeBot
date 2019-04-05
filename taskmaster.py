from dataclasses import dataclass
from typing import List
from discord.ext.commands.context import Context
import logging
import concurrent.futures
from battlefy.battlefy_scraper import scrape as battlefy_scrape, scrape_deep as battlefy_scrape_deep
from esl.esl import scrape as esl_scrape
from toornament.toornament_stalker import stalk as toornament_stalk

logger = logging.getLogger('scrap_logger')

# define the lookup table, should be updated when adding functions
b = "battlefy"
bd = "battlefy_deep"
e = "esl"
to = "toornament"
c = "challengermode"
call_list = [b, bd, e, to, c]
t = "TODAY"
w = "THIS WEEK"
we = "THIS WEEKEND"
time_frame_list = [t, w, we]
fiveVfive = "5v5"
threeVthree = "3v3"
oneVone = "1v1"
aram = "ARAM"
filter_list = [fiveVfive, threeVthree, oneVone, aram]

time_frame_lookup = {
    "today": t,
    "t": t,
    "w": w,
    "week": w,
    "this_week": w,
    "we": we,
    "weekend": we,
    "this_weekend": we
}

filter_lookup = {
    "5v5": fiveVfive,
    "3v3": threeVthree,
    "1v1": oneVone,
    "aram": aram
}

scrape_lookup = {
    "battlefy": b,
    "bat": b,
    "b": b,
    "battlefy_deep": bd,
    "bat_deep": bd,
    "bat_d": bd,
    "b_d": bd,
    "bd": bd,
    "esl": e,
    "e": e,
    "toornament": to,
    "to": to,
    "toor": to,
    "challengermode": c,
    "chal": c,
    "c": c,
    "challenger": c
}

stalk_lookup = {
    "toornament": to,
    "to": to,
    "toor": to
}

scrape_task_lookup = {
    b: battlefy_scrape,
    bd: battlefy_scrape_deep,
    e: esl_scrape
}

stalk_task_lookup = {
    to: toornament_stalk
}


@dataclass
class SingleTask:
    argument: str
    is_scrape: bool
    time_frame: str
    status: str = "WAITING"
    completed: bool = False

    def __str__(self):
        return self.argument


@dataclass
class TaskGroup:
    tasks: List[SingleTask]
    context: Context
    task_count: int = 0

    def __post_init__(self):
        self.task_count = len(self.tasks)


class UnknownArgumentError(Exception):
    """
    Raised when for a given argument no matching call or filter can be found
    """
    pass


def call_taskmaster(ctx: Context, args: List[str], is_scrape: bool):
    # call interpret_args to find the fitting tasks
    calls, filters, time_frame = interpret_args(ctx, args, is_scrape)
    logger.debug(
        "Interpreted args as calls: " + str(calls) + "\nand filters: " + str(filters) + "\nand time_frame: " + str(
            time_frame))

    # check for invalid amount of calls
    if len(calls) == 0:
        logger.debug("No viable calls in command, stopping...")
    if len(time_frame) > 1:
        logger.debug("Only one the first time_frame will be used")
    real_time_frame = time_frame[0]

    # create the SingleTask objects
    tasks = []
    for call in calls:
        task = SingleTask(call, is_scrape, real_time_frame)
        tasks.append(task)

    # create TaskGroup
    task_group = TaskGroup(tasks, ctx)

    # submit TaskGroup to multiprocessing
    logger.debug("Submitting TaskGroup with " + str(task_group.task_count) + " tasks")
    results = submit_task_group(task_group)

    # apply filter to results
    logger.debug("Applying filters to " + str(len(results)) + " tournaments")
    for filter_ in filters:
        results = results.filter_format(filter_)

    # return results to discord_bot
    logger.debug("Results are ready, " + str(len(results)) + " tournaments remain")
    return str(results)


def aliases_lookup(arg: str, is_scrape: bool):
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
        logger.warning("Unkwon argument found: " + real_arg)
        raise UnknownArgumentError

    # return the concrete arg or throw an unknown arg exception
    return real_arg


def split_calls_time_frame_filter(args: List[str]):
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


def interpret_args(ctx: Context, args: List[str], is_scrape: bool):
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


def execute_task(st: SingleTask):
    # use lookup to find scraper responsible for task
    st.status = "WORKING"
    if st.is_scrape:
        task = scrape_task_lookup.get(st.argument)
    else:
        task = stalk_task_lookup.get(st.argument)

    # let the scraper run and return the results
    result = task(time_frame=st.time_frame)
    st.status = "Finished"
    st.completed = True
    return result


def submit_task_group(tg: TaskGroup):
    results = []
    # setup ThreadPoolExecutor with worker pool and execute_task, also update the presence of the bot
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_task = {executor.submit(execute_task, task): task for task in tg.tasks}
        t_count = tg.task_count
        logger.debug(str(t_count) + " tasks have beend submitted.")
        for future in concurrent.futures.as_completed(future_to_task):
            t_count += -1
            logger.debug(str(t_count) + " tasks remaining")
            st = future_to_task[future]
            try:
                results.append(future.result())
            except Exception as exc:
                logger.error('%r generated an exception: %s' % (st, exc))

    # merge results into a single TournamentList
    total_tl = results.pop()
    for tl in results:
        total_tl.merge_tournament_lists(tl)

    # return results
    return total_tl
