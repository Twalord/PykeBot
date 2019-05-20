"""
Provides functions to collect information on all players in a SINN League Season.

:author: Jonathan Decker
"""
from utils.webmanager import open_session, quit_session
import logging
import time
import bs4
from models import Player, Team, TeamList, TeamListList
from utils import task_queue
from selenium.common.exceptions import ElementClickInterceptedException
import requests

logger = logging.getLogger('scrap_logger')


def stalk(url):
    """
    Main function of the module, takes a url to a SINN League Season and returns a list of TeamList objects
    :param url: Str, url to the main page of a SINN League Season
    :return: List[TeamList], a list of TeamList objects with each TeamList representing a group
    """
    # open web session
    driver = open_session()

    driver.get(url)

    # Select Gruppenphase Container
    div_button_list = driver.find_elements_by_class_name("content-subsection-toggle")
    # division 1 and 2 are expanded by default
    count = 4
    for div_button in reversed(div_button_list):
        if count > 0:
            try:
                div_button.click()
            except ElementClickInterceptedException:
                button = driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/div/button[2]")
                button.click()
                time.sleep(1)

                div_button.click()
        count += -1

    soup = bs4.BeautifulSoup(driver.page_source, features="html.parser")
    box_container = soup.find_all('section', class_="boxed-section")
    gruppenphase = "Gruppenphase"
    for box in box_container:
        title = box.find_all("h2")
        if len(title) > 0:
            if gruppenphase in title[0].text:
                group_stage_container = box

    # extract all group-links
    links = [link["href"] for link in group_stage_container.find_all("a", href=True)]
    links = list(dict.fromkeys(links))

    links = filter(filter_links, links)

    # close web session
    quit_session(driver)

    # create task Q over all group-links
    single_tasks = []
    for link in links:
        single_task = task_queue.SingleTask(stalk_group, link)
        single_tasks.append(single_task)
    task_group = task_queue.TaskGroup(single_tasks, "stalk: " + url)

    logger.info("Stalking " + str(len(single_tasks)) + " groups in SINN League")
    team_lists = task_queue.submit_task_group(task_group)

    # return results
    logger.info("Finished SINN League stalking")
    return TeamListList(team_lists)


def filter_links(link):
    """
    Helper function to filter out non group links
    :param link: Str, a web link
    :return: Bool, true if the link contains a keyword and leads to a group, false if not
    """
    keywords = ["gruppenphase", "group"]
    link_split = link.split("/")
    for split in link_split:
        if split in keywords:
            return True
    return False


def stalk_group(url):
    """
    Returns a TeamList object for all teams in the group behind the given url.
    :param url: Str, a link to a group in a SINN League
    :return: TeamList, a TeamList object containing all teams of the group
    """
    # open web session
    page = requests.get(url)

    # Select Rangliste Container and find division name
    soup = bs4.BeautifulSoup(page.text, features="html.parser")
    list_container = soup.find('table', class_="table table-fixed-single table-responsive")
    # div_name = driver.find_element_by_xpath("//*[@id=\"container\"]/div/h1").text
    div_name = soup.select("#container > div > h1")[0].text

    # extract all team-links
    links = [link["href"] for link in list_container.find_all("a", href=True)]
    links = list(dict.fromkeys(links))

    # create task Q over all team-links
    single_tasks = []
    for link in links:
        single_task = task_queue.SingleTask(stalk_team, link)
        single_tasks.append(single_task)
    task_group = task_queue.TaskGroup(single_tasks, "stalk: " + div_name)

    teams = task_queue.submit_task_group(task_group)

    # return results
    for team in teams:
        if team is None:
            teams.remove(team)
    return TeamList(div_name, teams)


def stalk_team(url):
    """
    Returns a Team object for all players in the team behind the given url
    :param url: Str, a link to a team on the SINN League page
    :return: Team, a Team object containing all valid players from the Team
    """
    # open web session
    page = requests.get(url)

    # Select Teammitglieder Container and find team name
    soup = bs4.BeautifulSoup(page.text, features="html.parser")
    player_container = soup.find('ul', class_="content-portrait-grid-l")

    # check if the team was deleted
    if player_container is None:
        return None
    team_container = soup.find('div', class_="content-portrait-head")
    team_name = team_container.find("a").text

    # extract player names
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

    # return results
    return team_obj
