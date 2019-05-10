import logging
import bs4
from models import Player, Team, TeamList, Rank
from utils import task_queue
import requests

from utils.lookup_tables import rank_lookup, rating_lookup

logger = logging.getLogger('scrap_logger')


def calc_average_max_rank(team):
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


def add_list_team_list_ranks(team_lists):
    single_tasks = []
    for team_list in team_lists:
        single_tasks.append(task_queue.SingleTask(add_team_list_ranks, team_list))

    task_group = task_queue.TaskGroup(single_tasks)
    task_queue.submit_task_group(task_group)


def add_team_list_ranks(team_list: TeamList):
    teams = team_list.teams
    single_tasks = []
    for team in teams:
        single_tasks.append(task_queue.SingleTask(add_team_ranks, team))

    task_group = task_queue.TaskGroup(single_tasks)
    task_queue.submit_task_group(task_group)


def add_team_ranks(team: Team):
    player_list = team.player_list
    updated_list = []
    for player in player_list:
        updated_list.append(add_player_rank(player))
    team.player_list = updated_list
    team = calc_average_max_rank(team)
    return team


def add_player_rank(player: Player):
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
    base_url = "https://lolprofile.net/summoner/euw/"
    url = base_url + sum_name.replace(" ", "%20")
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.text, features="html.parser")
    elo = soup.find('span', class_="tier")
    if elo is not None:
        return elo.text
    else:
        return "Unranked"


def stalk_player_opgg(sum_name):
    base_url = "https://euw.op.gg/summoner/userName="
    url = base_url + sum_name.replace(" ", "+")
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.text, features="html.parser")
    elo = soup.find('div', class_="TierRank")
    if elo is not None:
        return elo.text
    else:
        return "Unranked"


def stalk_player_mobalytics(sum_name):
    base_url = "https://lol.mobalytics.gg/summoner/euw/"
    url = base_url + sum_name.replace(" ", "%20")
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.text, features="html.parser")
    elo = soup.find('p', class_="profilestyles__TierInfoLabel-y97g0w-19 jCyjuF")
    if elo is not None:
        return elo.text
    else:
        return "Unranked"


def stalk_player_leagueofgraphs(sum_name):
    base_url = "https://www.leagueofgraphs.com/summoner/euw/"
    url = base_url + sum_name.replace(" ", "+")
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.text, features="html.parser")
    elo = soup.find('span', class_="leagueTier")
    if elo is not None:
        return elo.text
    else:
        return "Unranked"
