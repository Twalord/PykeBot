"""
Provides functions to look up player rankings online and calculate average team rankings

:author: Jonathan Decker
"""

import logging
import bs4
from models import Player, Team, TeamList, Rank, TeamListList
from utils import task_queue
import requests
from utils import scrap_config as config

from utils.lookup_tables import rank_lookup, rating_lookup

logger = logging.getLogger('scrap_logger')


def calc_average_max_rank(team):
    """
    Calculates the average and max player rank for a given team and sets it for the team
    :param team: Team, a Team object containing a list of players with set ranks
    :return: Team, the same object that was given but with its average and max rank set
    """
    ranks = []
    for player in team.player_list:
        if player.rank is not None and player.rank.rating > 0:
            ranks.append(player.rank)
    count = len(ranks)
    rank_sum = 0
    list_ratings = []
    for rank in ranks:
        rank_sum += rank.rating
        list_ratings.append(rank.rating)
    if count == 0:
        average = 0
        max_rank = 0
    else:
        average = round(rank_sum / count)
        max_rank = max(list_ratings)
    team.average_rank = Rank(rating_lookup.get(average), average)
    team.max_rank = Rank(rating_lookup.get(max_rank), max_rank)
    return team


def add_list_team_list_ranks(team_list_list: TeamListList):
    """
    Calls add_team_lists_ranks for every given team_list
    :param team_lists: List[TeamList], a list of TeamList objects
    :return: None, but the Team and Player objects inside were modified
    """
    single_tasks = []
    for team_list in team_list_list.team_lists:
        single_tasks.append(task_queue.SingleTask(add_team_list_ranks, team_list))

    task_group = task_queue.TaskGroup(single_tasks, "add ranks to team lists")
    task_queue.submit_task_group(task_group)


def add_team_list_ranks(team_list: TeamList):
    """
    Calls add_team_ranks for every Team in the TeamList
    :param team_list: TeamList, a TeamList object containing a list of Teams
    :return: None, but the Team and player objects inside were modified
    """
    teams = team_list.teams
    single_tasks = []
    for team in teams:
        single_tasks.append(task_queue.SingleTask(add_team_ranks, team))

    task_group = task_queue.TaskGroup(single_tasks, "add ranks to team list")
    task_queue.submit_task_group(task_group)


def add_team_ranks(team: Team):
    """
    Calls add_player_rank and calc_average_max_rank on the given Team object
    :param team: Team, a Team object with a set list of players
    :return: Team, the same object with added ranks for the players and average and max rank for the team
    """
    player_list = team.player_list
    updated_list = []
    for player in player_list:
        updated_list.append(add_player_rank(player))
    team.player_list = updated_list
    team = calc_average_max_rank(team)
    return team


def add_player_rank(player: Player):
    """
    Call stalk player functions and adds a Rank to the given Player
    :param player: Player, a Player object with a summoner_name
    :return: Player, Player object with the same summoner_name and a set Rank
    """
    sum_name = player.summoner_name
    elo = stalk_player_opgg(sum_name).lower()
    if elo in rank_lookup:
        rating = rank_lookup.get(elo)
    else:
        rating = 0
    rank = Rank(rating_lookup.get(rating), rating)
    return Player(player.summoner_name, rank)


def test_stalk_player(sum_name):
    print("mobalytics: " + stalk_player_mobalytics(sum_name))
    print("leagueofgraphs: " + stalk_player_leagueofgraphs(sum_name))
    print("lolprofile: " + stalk_player_lolprofile(sum_name))
    print("opgg: " + stalk_player_opgg(sum_name))


def stalk_player_lolprofile(sum_name):
    """
    Use lolprofile web page to find the the current soloQ ranking for the given summoner name
    :param sum_name: Str, the summoner name of a league game account
    :return: Str, string version of the ranking
    """
    region = config.get_region()
    base_url = f"https://lolprofile.net/summoner/{region}/"
    url = base_url + sum_name.replace(" ", "%20")
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.text, features="html.parser")
    elo = soup.find('span', class_="tier")
    if elo is not None:
        return elo.text
    else:
        return "Unranked"


def stalk_player_opgg(sum_name):
    """
    Use op.gg web page to find the the current soloQ ranking for the given summoner name
    :param sum_name: Str, the summoner name of a league game account
    :return: Str, string version of the ranking
    """
    region = config.get_region()
    base_url = f"https://{region}.op.gg/summoner/userName="
    url = base_url + sum_name.replace(" ", "+")
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.text, features="html.parser")
    elo = soup.find('div', class_="TierRank")
    if elo is not None:
        return elo.text
    else:
        return "Unranked"


def stalk_player_mobalytics(sum_name):
    """
    Use mobalytics web page to find the the current soloQ ranking for the given summoner name
    :param sum_name: Str, the summoner name of a league game account
    :return: Str, string version of the ranking
    """
    region = config.get_region()
    base_url = f"https://lol.mobalytics.gg/summoner/{region}/"
    url = base_url + sum_name.replace(" ", "%20")
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.text, features="html.parser")
    elo = soup.find('p', class_="profilestyles__TierInfoLabel-y97g0w-19 jCyjuF")
    if elo is not None:
        return elo.text
    else:
        return "Unranked"


def stalk_player_leagueofgraphs(sum_name):
    """
    Use leagueofgraphs web page to find the the current soloQ ranking for the given summoner name
    :param sum_name: Str, the summoner name of a league game account
    :return: Str, string version of the ranking
    """
    region = config.get_region()
    base_url = f"https://www.leagueofgraphs.com/summoner/{region}/"
    url = base_url + sum_name.replace(" ", "+")
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.text, features="html.parser")
    elo = soup.find('span', class_="leagueTier")
    if elo is not None:
        return elo.text
    else:
        return "Unranked"
