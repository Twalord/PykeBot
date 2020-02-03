"""
Handles interpreting commands and calling the respective stalker

:author: Jonathan Decker
"""
import logging
from stalker import challengermode_stalker, sinn_league_stalker, toornament_stalker, premiertour_stalker
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


def feature_not_available_right_now(*args):
    return "This feature is not available in the current version"


def call_stalk_master(url, extended=False, discord_format=True) -> str:
    """
    Oversees stalking of the given url and returns the results as string.
    :param url: String, a valid url for any stalker. If it can't be matched an error message will be returned.
    :param extended: Boolean(False), flag to set if player look ups should be run for the players found.
    :param discord_format: Boolean(True), flag to set if the returned string should be formatted for discord chat.
    :return:
    """
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
    if extended:
        if isinstance(results, TeamListList):
            player_lookup.add_list_team_list_ranks(results)
        elif isinstance(results, TeamList):
            player_lookup.add_team_list_ranks(results)
        elif isinstance(results, Team):
            player_lookup.add_team_ranks(results)

        if isinstance(results, str):
            out = results
        else:
            if discord_format:
                out = results.extended_str()
            else:
                out = results.ext_no_format_str()

    else:
        if discord_format:
            out = str(results)
        else:
            out = results.no_format_str()

    return out


def url_matcher(url):
    """
    Analyses the given url and returns a stalker function for it.
    :param url: String, a valid url. Will raise error if no stalker could be found.
    :return: function, a stalker function which is able to anaylse the given url.
    """
    website = None
    # use lookup table to find matching website and stalker
    website_keywords = ["challengermode", "toornament", "summoners-inn", "primeleague"]
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
        match_keywords = ["games"]
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

    if website is "primeleague":
        league_keywords = ["leagues"]
        if all(elem in url.split("/") for elem in league_keywords):
            website_type = "league"
        else:
            raise UnknownUrlError

    logger.debug(url + " has been detected as " + website + " and " + website_type)

    stalker_lookup = {"challengermode": {"match": challengermode_stalker.quick_stalk,
                                         "tournament": feature_not_implemented_yet},
                      "toornament": {"tournament": toornament_stalker.stalk},
                      "summoners-inn": {"season": sinn_league_stalker.stalk,
                                        "group": sinn_league_stalker.stalk_group,
                                        "team": sinn_league_stalker.stalk_team},
                      "primeleague": {"league": premiertour_stalker.stalk}}

    stalker = stalker_lookup.get(website).get(website_type)
    return stalker
