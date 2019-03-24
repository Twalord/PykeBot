import scrap_config as config
import logging
from selenium import webdriver
import bs4
import time


logger = logging.getLogger('scrap_logger')


def stalk_toornament(toornament_link):
    """
    Stalks all teams signed up for the given toornament and returns an op.gg multi link for each team
    :param toornament_link: String, url to a tournament on toornament
    :return: List[String], containing the op.gg multi links for each team
    """

    # open the websession
    driver = webdriver.Firefox()
    driver.implicitly_wait(30)
    driver.get(toornament_link)

    # find the participants button and press it
    participants_button = driver.find_element_by_xpath("//*[@id=\"tournament-nav\"]/div/section/div/ul/li[2]/a")
    participants_button.click()
    time.sleep(2)

    # find all teams and save the links
    participants_links = []
    base_url = "https://www.toornament.com"
    toornament_soup = bs4.BeautifulSoup(driver.page_source, features="html.parser")
    team_container = toornament_soup.find_all('div', class_="size-1-of-4")

    for team in team_container:
        a = team.find('a', href=True)
        participants_links.append(base_url + a['href'])

    # open each link, switch to information and collect the Summoner Names
    multi_links = []
    for link in participants_links:
        driver.get(link)
        time.sleep(0.5)
        information_button = driver.find_element_by_xpath("//*[@id=\"main-container\"]/div[2]/section/ul/li[1]/a")
        information_button.click()
        time.sleep(0.5)
        toornament_soup = bs4.BeautifulSoup(driver.page_source, features="html.parser")
        name_container = toornament_soup.find_all('div', class_="text secondary small summoner_player_id")
        names = []
        for container in name_container:
            dirty_string = container.text
            dirt, name = dirty_string.split(":")
            name = name.replace("\n", "")
            name = name.strip()
            names.append(name)
        multi_links.append(build_opgg_multi_link(names))

    driver.quit()
    return multi_links


def build_opgg_multi_link(sum_names):
    """
    construct a valid op.gg multi link for the given summoner names
    :param sum_names: List[String], a list of Summonernames
    :return: String, url to the multilink for the given names
    """
    region = "euw"  # static for now, should be loaded from config
    base_url = "https://" + region + ".op.gg/multi/query="
    multi_link = base_url
    for sum_name in sum_names:
        multi_link += sum_name.replace(" ", "")
        multi_link += "%2C"
    return multi_link
