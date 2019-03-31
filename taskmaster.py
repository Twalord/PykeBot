from dataclasses import dataclass
from typing import List
from discord.ext.commands.context import Context


@dataclass
class SingleTask:
    arguments: List[str]
    status: str = "WAITING"
    completed: bool = False


@dataclass
class TaskGroup:
    tasks: List[SingleTask]
    task_count: int
    context: Context


def call_taskmaster(ctx: Context, args: str, is_scrape: bool):
    pass
    # split args

    # call interpret_args to find the fitting tasks

    # create the SingleTask objects

    # create TaskGroup

    # submit TaskGroup to multiprocessing

    # apply filter to results

    # send context and results to discord_bot


def aliases_lookup(arg: str):
    pass
    # use dict to find concrete arg

    # return the concrete arg or throw an unknown arg exception


def interpret_args(args: List[str], is_scrape: bool):
    pass
    # use lookup table to understand aliases

    # split calls and filter

    # return tuple with args for calls and filter


def task_loopup(arg: str):
    pass
    # use dict to find the function

    # return the function or throw an unknown func exception


def execute_task(st: SingleTask):
    pass
    # use lookup to find scraper responsible for task

    # let the scraper run and return the results


def submit_task_group(tg: TaskGroup):
    pass
    # setup ThreadPoolExecutor with worker pool and execute_task

    # start worker pool and collect results

    # return results
