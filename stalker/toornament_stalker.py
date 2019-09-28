"""
Handles scraping of the toornament page.
:author: Jonathan Decker
"""
import logging
import bs4
from models import Team, TeamList, Player
import requests
from utils.task_queue import TaskGroup, SingleTask, submit_task_group


logger = logging.getLogger('scrap_logger')


def stalk(toornament_link):
    """
    Stalks all teams signed up for the given toornament and returns a TeamList Object
    :param toornament_link: String, url to a tournament on toornament
    :return: TeamList, containing the Team obj for each signed up team
    """

    logger.debug("Beginning toornament stalk for " + toornament_link)
    # edit the link
    toornament_link_list = toornament_link.split("/")[:-1]
    toornament_link_list.append("participants")
    edited_toornament_link = "/".join(toornament_link_list)

    # find all teams and save the links
    participants_links = []
    base_url = "https://www.toornament.com"
    page = requests.get(edited_toornament_link)
    toornament_soup = bs4.BeautifulSoup(page.text, features="html.parser")
    team_container = toornament_soup.find_all('div', class_="size-1-of-4")

    # multiple team page test
    multipage_toornament = edited_toornament_link +"?page=1"
    count = 1
    while True:
        count += 1
        #driver.get(str(driver.current_url)[:-1] + str(count))
        multipage_toornament = multipage_toornament[:-1] + str(count)
        page = requests.get(multipage_toornament)
        toornament_soup2 = bs4.BeautifulSoup(page.text, features="html.parser")
        if len(toornament_soup2.find_all('div', class_="size-1-of-4")) > 0:
            team_container.extend(toornament_soup2.find_all('div', class_="size-1-of-4"))
        else:
            break

    # extract toornament name
    tournament_name = toornament_soup.select("#main-container > div.layout-section.header > div > section > div > div.information > div.name > h1")[0].text

    for team in team_container:
        a = team.find('a', href=True)
        participants_links.append(base_url + a['href'])

    # open each link, switch to information and collect the Summoner Names
    single_tasks = []
    for link in participants_links:
        single_tasks.append(SingleTask(stalk_team, link))
    task_group = TaskGroup(single_tasks, "stalk: " + tournament_name)

    teams_players_tuples = submit_task_group(task_group)

    # build Player, Team and TeamList objects
    team_list = []
    for team in teams_players_tuples:
        sum_names = team[0]
        team_name = team[1]
        players = []
        for sum_name in sum_names:
            players.append(Player(sum_name))
        team_list.append(Team(team_name, players))

    return TeamList(tournament_name, team_list)


def stalk_team(url):
    """
    Use request to gather information on a team on toornament
    :param url: Str, url to the main page of a team
    :return: (List[Str], Str), a tuple containing the list of player names and the team name
    """

    logger.debug("Beginning toornament team stalk for " + url)
    edited_url = url + "info"
    page = requests.get(edited_url)

    toornament_soup = bs4.BeautifulSoup(page.text, features="html.parser")
    team_name = toornament_soup.select("#main-container > div.layout-section.header > div > div.layout-block.header > div > div.title > div > span")[0].text
    name_container = toornament_soup.find_all('div', class_="text secondary small summoner_player_id")

    names = []
    for container in name_container:
        dirty_string = container.text
        dirt, name = dirty_string.split(":")
        name = name.replace("\n", "")
        name = name.strip()
        names.append(name)
    return names, team_name
