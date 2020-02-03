"""
Handles scraping of primeleague.gg since premiertour rebranded to primeleague.

:author: Jonathan Decker
"""

import logging
import bs4
from bs4.diagnose import diagnose
from models import Team, TeamList, Player
import requests
from utils.task_queue import TaskGroup, SingleTask, submit_task_group


logger = logging.getLogger('scrap_logger')


def stalk(premiertour_link):
    """
    Stalks all teams signed up for the given premiertour tournament, only uses requests
    :param premiertour_link: String, valid url to the main page of the premiertour tournament
    :return: TeamList, containing the Team obj for each signed uo team
    """

    logger.debug("Beginning stalk for " + premiertour_link)

    # find the name of the tournament
    tournament_name = get_title(premiertour_link)

    # edit the link
    premiertour_link_list = premiertour_link.split("/")
    premiertour_link_list.append("participants")
    edited_premiertour_link = "/".join(premiertour_link_list)

    # find all teams and save the links
    # find first div class=list-section to only consider valid participants
    # grab div class=section-content from it and extract all hrefs
    all_links = grab_team_links(edited_premiertour_link)

    # open each link, collect summoner names
    single_tasks = []
    for link in all_links:
        single_tasks.append(SingleTask(stalk_team, link))
    task_group = TaskGroup(single_tasks, "stalk: " + tournament_name)

    team_list = submit_task_group(task_group)

    return TeamList(tournament_name, team_list)


def stalk_team(url):
    """
    Takes the url to a premiertour team page and returns a Team obj for the players of the team
    :param url: String, valid link to a premiertour team page
    :return: Team, containing the players of the team
    """
    # request page information
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.text, features="html.parser")
    player_container = soup.find('ul', class_="content-portrait-grid-l")

    # check if the team was deleted
    if player_container is None:
        return None

    # collect team name
    team_name = soup.find("h1").text

    # collect player names
    player_boxes = player_container.find_all('li')
    tuple_list = []
    for box in player_boxes:
        confirmed = box.find('span', class_="txt-status-positive")
        player_info = box.find('span', title="League of Legends » LoL Summoner Name (EU West)")
        tuple_list.append((player_info, confirmed))

    # create Team object and filter out unconfirmed player
    player_names = []
    confirmed_check = "Bestätigter Spieler"
    for player, confirm in tuple_list:
        if confirm is not None and confirm.text == confirmed_check:
            player_obj = Player(player.text)
            player_names.append(player_obj)
    team_obj = Team(team_name, player_names)

    return team_obj


def get_title(url):
    """
    Takes the link to the premiertour main page and returns the title of the tournament
    :param url: String, valid link to the main page of a premiertour tournament
    :return: String, the title of the tournament
    """

    main_page = requests.get(url)
    main_premiertour_soup = bs4.BeautifulSoup(main_page.text, features="html.parser")
    tournament_name = main_premiertour_soup.find("h1").text
    return tournament_name


def grab_team_links(url):
    """
    Takes the url to the participants page of a premiertour tournament and returns all links to valid teams
    :param url: String, valid link to the participants page of a premiertour tournament
    :return: List(String), list of urls to all teams with valid sign ups
    """
    page = requests.get(url)
    html_string = page.text
    premiertour_soup = bs4.BeautifulSoup(html_string, features="html.parser")
    team_container = premiertour_soup.find_all("tr")

    links = []
    for container in team_container:
        # checks if the second table with incomplete sign ups has been reached
        table_check = container.find("span", class_="table-cell-item txt-status-pending")
        if table_check:
            if "Nicht genug Spieler" in table_check.text:
                continue
        links.extend([link["href"] for link in container.find_all("a", href=True)])
    return list(dict.fromkeys(links))
