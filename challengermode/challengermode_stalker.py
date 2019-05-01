from webmanager import open_session, quit_session
import logging
import time
import bs4

logger = logging.getLogger('scrap_logger')


def stalk(challengermode_link):

    # open a websession
    driver = open_session(headless=False)
    driver.get(challengermode_link)

    # find the teams button and press it
    teams_button = driver.find_element_by_xpath("//*[@id=\"arena-wrap\"]/div[3]/div[3]/div[3]/div/div[1]/a[4]")
    teams_button.click()
    time.sleep(0.5)

    """
    each dropdown has to be opened one at a time, as they will be closed again automatically
    lazy loading is used and it needs to be scrolled down to load more elements

    solution use a counter
    1. scroll down and collect all team names and assign numbers to them (not all teams are shown at the same time)
    2. iterate over the team names via the class cm-component
    3. use click to open dropdown and download html doc again
    4. extract div class="p-b--small p-h--base p-h--small--md p-h--none--sm"
    5. scroll down to keep loading all teams
    6. extract infos from each container and create objects
    """

    team_container = []
    teams_dropdown = driver.find_elements_by_class_name("cm-component")
    for dropdown in teams_dropdown:
        dropdown.click()
        time.sleep(0.5)
        #container = driver.find_element_by_class_name("bor--bot bor--gray bg--gray-dark--30 c--white")
        #team_container.append(container)
        dropdown.click()
        time.sleep(0.1)

    # open exception if no more teams are on page

    # save each team name and their number as triple with number, name, None

    # iterate over the triples scrolling down if not on page

    # open dropdown reload the page

    # extract container and save it to the 3rd space of the triple

    # close the dropdown reload the page



    # iterate through all container extracting all player names and the team name
    for container in team_container:
        team_name = bs4.BeautifulSoup(container).find('a', class_="link-white").text
        print(team_name)
        print(container)

    quit_session(driver)