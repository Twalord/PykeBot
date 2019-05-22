"""
Handles interpreting commands and calling the respective stalker

:author: Jonathan Decker
"""
import logging
from challengermode import challengermode_stalker
from toornament import toornament_stalker
from sinn_league import sinn_league_stalker
from utils import task_queue, player_lookup
from models import Team, TeamList, TeamListList


logger = logging.getLogger('scrap_logger')


class UnknownUrlError(Exception):
    """
    Raised when for a given url no matching stalker can be found
    """
    pass


def feature_not_implemented_yet(*args):
    return "This feature is not ready yet."


def call_stalk_master(url, extendend=False) -> str:
    # call url matcher to find out which stalker to use
    try:
        stalker = url_matcher(url)
        logger.debug(url + " will be handled by " + stalker.__name__)
    except UnknownUrlError:
        logger.warning("User submitted an invalid url: " + url)
        return f"The given URL could not be matched with any available tool. The URL was: {url}"

    # create task for stalker
    single_task = [task_queue.SingleTask(stalker, url)]
    task_group = task_queue.TaskGroup(single_task, stalker.__name__)

    results = task_queue.submit_task_group(task_group)[0]

    # prepare output
    if extendend:
        if isinstance(results, TeamListList):
            player_lookup.add_list_team_list_ranks(results)
        elif isinstance(results, TeamList):
            player_lookup.add_team_list_ranks(results)
        elif isinstance(results, Team):
            player_lookup.add_team_ranks(results)

        out = results.extended_str()

    else:
        out = str(results)

    # return
    return out


def url_matcher(url):
    website = None
    # use lookup table to find matching website and stalker
    website_keywords = ["challengermode", "toornament", "summoners-inn"]
    for keyword in website_keywords:
        if keyword in url:
            website = keyword
            break

    if website is None:
        raise UnknownUrlError

    website_type = None

    # checks are duplicated could be solved as for loop but due to small size should be fine this way
    if website is "challengermode":
        tournament_keywords = ["Tournaments", "Show"]
        match_keywords = ["Challenges", "View"]
        if all(elem in url.split("/") for elem in tournament_keywords):
            website_type = "tournament"
        elif all(elem in url.split("/") for elem in match_keywords):
            website_type = "match"
        else:
            raise UnknownUrlError

    if website is "toornament":
        tournament_keywords = ["tournaments", "information"]
        if all(elem in url.split("/") for elem in tournament_keywords):
            website_type = "tournament"
        else:
            raise UnknownUrlError

    if website is "summoners-inn":
        group_keywords = ["leagues", "group"]
        team_keywords = ["leagues", "teams"]
        season_keywords = ["leagues"]
        if all(elem in url.split("/") for elem in group_keywords):
            website_type = "group"
        elif all(elem in url.split("/")for elem in team_keywords):
            website_type = "team"
        elif all(elem in url.split("/") for elem in season_keywords):
            website_type = "season"
        else:
            raise UnknownUrlError

    logger.debug(url + " has been detected as " + website + " and " + website_type)

    stalker_lookup = {"challengermode": {"match": challengermode_stalker.quick_stalk,
                                         "tournament": feature_not_implemented_yet},
                      "toornament": {"tournament": toornament_stalker.stalk},
                      "summoners-inn": {"season": sinn_league_stalker.stalk,
                                        "group": sinn_league_stalker.stalk_group,
                                        "team": sinn_league_stalker.stalk_team}}

    stalker = stalker_lookup.get(website).get(website_type)
    return stalker
