"""
Offers multi threading functionality, simply import SingleTask, TaskGroup and submit_task_group,
create a list of SingleTasks with the function as the first arg and the args for that function as the other args.
Now create a TaskGroup from that list and use it as a parameter for submit_task_group.
This will run each SingleTask as an individual Thread and submit_task_group will return a list with the results for each
SingleTask.
:author: Jonathan Decker
"""
import concurrent.futures
from typing import List
import logging
import traceback

logger = logging.getLogger('scrap_logger')


class SingleTask:

    def __init__(self, func, *args):
        self.func_pos0 = []
        self.args = args
        self.func_pos0.append(func)

    def __str__(self):
        return str(self.args)

    def execute(self):
        func = self.func_pos0[0]
        arguments = self.args
        result = func(*arguments)
        return result


class TaskGroup:

    def __init__(self, tasks: List[SingleTask]):
        self.task_count = len(tasks)
        self.tasks = tasks


def submit_task_group(tg: TaskGroup, max_workers=20):
    """
    Submits all tasks in the given TaskGroup to a ThreadPoolExecutor and returns the merged results
    :param tg: Taskgroup, a valid Taskgroup
    :param max_workers: int, set the limit for parallel workers, standard is 20
    :return: TournamentList, merged from the TournamentList objects returned by the tasks in the TaskGroup
    """
    results = []
    # setup ThreadPoolExecutor with worker pool and execute_task, also update the presence of the bot
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {executor.submit(task.execute): task for task in tg.tasks}
        t_count = tg.task_count
        logger.debug(str(t_count) + " tasks have been submitted.")
        for future in concurrent.futures.as_completed(future_to_task):
            t_count += -1
            logger.debug(str(t_count) + " tasks remaining")
            st = future_to_task[future]
            try:
                results.append(future.result())
            except Exception as exc:
                traceback_string = traceback.format_exc()
                logger.error('%r generated an exception: %s' % (st, exc))
                logger.debug(traceback_string)

    # return results
    return results
