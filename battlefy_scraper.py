import bs4
import logging
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
import time
from models import BattlefyTournament, BattlefyTournamentList, DeepBattlefyTournament
import pytz
import datetime
import scrap_config as config

logger = logging.getLogger('scrap_logger')


def scrape(scrape_deep=False):
    # returns a BattlefyTournament list object based on the information scraped from the battlefy site
    # deep search returns additional information like the link to the tournament but takes longer
    logger.debug("Selected Websites: " + str(config.get_websites()))

    battlefy_tournaments_list = BattlefyTournamentList([])

    if "BATTLEFY" not in config.get_websites():
        logger.warning("Battlefy scraper is disabled.")
        return battlefy_tournaments_list

    regions = config.get_regions()
    if len(regions) == 0:
        logger.warning("No region selected.")
        return battlefy_tournaments_list

    for region in regions:
        battlefy_tournaments = []
        logger.debug("using " + region + "_URL")
        url = config.get_battlefy_url(region)
        driver = open_session(url)

        select_time_frame(driver)
        load_more(driver)

        battlefy_soup = bs4.BeautifulSoup(driver.page_source, features="html.parser")
        tournament_container = battlefy_soup.find_all('div', class_="card-container")
        if not scrape_deep:
            driver.quit()

            battlefy_tournaments += extract_container(tournament_container, region)

            battlefy_tournaments_list.append_tournaments(battlefy_tournaments)

        else:
            logger.debug("Starting deep search")
            battlefy_tournaments += extract_container(tournament_container, region, scrape_deep=True)

            for battlefy_tournament in battlefy_tournaments:
                link = find_link(battlefy_tournament.name, battlefy_tournament.host, driver)
                battlefy_tournament.link = link

            driver.quit()

            battlefy_tournaments_list.append_tournaments(battlefy_tournaments)

    return battlefy_tournaments_list


def open_session(url):
    # opens a web session and returns the webdriver
    driver = webdriver.Firefox()
    driver.implicitly_wait(30)
    logger.debug("Opening " + url + " in selenium firefox session")
    driver.get(url)

    return driver


def select_time_frame(driver):
    # Battlefy offers TODAY, THIS WEEK and THIS WEEKEND as preset filters
    # selects the filter in the webdriver based on the selection in the configs
    time_frame = config.get_battlefy_time_frame()
    logger.debug("Selected time_frame: " + time_frame)
    if time_frame == "THIS_WEEK":
        button = driver.find_element_by_xpath("/html/body/bf-app/main/div/div/bf-browse/div/bf-tournament-filters/div/bf-tournament-time-filters/bf-tab-bar/div/div[2]")
        button.click()
        time.sleep(2)
        return
    elif time_frame == "THIS_WEEKEND":
        button = driver.find_element_by_xpath("/html/body/bf-app/main/div/div/bf-browse/div/bf-tournament-filters/div/bf-tournament-time-filters/bf-tab-bar/div/div[3]")
        button.click()
        time.sleep(2)
        return
    elif time_frame != "TODAY":
        logger.error("Invalid TIME_FRAME for battlefy scraper, defaulting to TODAY")
    button = driver.find_element_by_xpath("/html/body/bf-app/main/div/div/bf-browse/div/bf-tournament-filters/div/bf-tournament-time-filters/bf-tab-bar/div/div[1]")
    button.click()
    time.sleep(2)


def handle_iframe_popup(driver):
    # sometimes after a while an iframe popup appears which needs to be closed in order to continue
    logger.debug("Trying to handle iframe popup.")
    driver.switch_to.frame("intercom-modal-frame")
    close_button = driver.find_element_by_xpath("/html/body/div/div/span/div/div/div[2]/div/div/div/span")
    time.sleep(2)
    close_button.click()
    driver.switch_to.default_content()


def load_more(driver):
    # presses load more button until all tournaments for the time_frame are loaded
    while True:
        try:
            load_more_button = driver.find_element_by_xpath(
                "//*[@id=\"ng-app\"]/body/bf-app/main/div/div/bf-browse/div/bf-tournament-card-list/div[2]/button")
            load_more_button.click()
            time.sleep(2)

        except NoSuchElementException:
            break
        except ElementNotInteractableException:
            break
        # Handles the annoying popup by closing it
        except ElementClickInterceptedException:
            handle_iframe_popup(driver)
            continue


def extract_container(tournament_container, region, scrape_deep=False):
    # returns a list of BattlefyTournament objects created from the collected information
    battlefy_tournament_list = []
    # Selects name, date, time and type for each tournament
    for tournament in tournament_container:
        name = tournament.find('h4', class_="text-16px font-400 text-white").text
        table = tournament.find_all('table')

        # table contains two tables the first contains the date and time
        tds = []
        for tr in table[0].find_all('tr'):
            td2 = tr.find_all('td')
            for td in td2:
                tds.append(td)

        date = tds[1].text
        time = tds[3].text

        # the second table contains the region and type
        tds = []
        for tr in table[1].find_all('tr'):
            td2 = tr.find_all('td')
            for td in td2:
                tds.append(td)

        # type is reserved so ttype for tournament type
        ttype = tds[3].text

        date_time = time_converter(date, time)

        host = tournament.find('span', class_="text-16px ellipsis font-400 text-white ml-10 org-name").text

        if not scrape_deep:
            battlefy_tournament = BattlefyTournament(name=name, date_time=date_time, region=region, ttype=ttype,
                                                     host=host)
        else:
            battlefy_tournament = DeepBattlefyTournament(name=name, date_time=date_time, region=region, ttype=ttype,
                                                         host=host)
        battlefy_tournament_list.append(battlefy_tournament)

    logger.debug("A total of " + str(len(tournament_container)) + " tournaments were found.")

    return battlefy_tournament_list


def time_converter(date, time):
    # date has form: Sun, Feb 17th
    # time has form: 2:00 PM GMT
    date_list = date.split()
    # weekday is ignored
    month = date_list[1]
    # removes the 'st', 'nd', 'th' from the string
    day = date_list[2][:-2]
    time_list = time.split()
    time24 = time_list[0]
    # convert PM to 24 hours
    if time_list[1] == "PM":
        time24_list = time24.split(':')
        hours = int(time24_list[0]) + 12
        # 24 is not accepted so needs to be changed to 0 and day + 1
        if hours == 24:
            hours = 0
            day = str(int(day) + 1)
        # for the datetime conversion hours must be 2 digits
        if len(str(hours)) == 1:
            time24 = "0" + str(hours) + ":" + time24_list[1]
        else:
            time24 = str(hours) + ":" + time24_list[1]
    # for the datetime conversion day must be 2 digits
    if len(day) == 1:
        day = "0" + day
    # adding seconds
    time24 = time24 + ":00"
    timezone = time_list[2]
    # get the number of the month
    month_int = convert_month(month)
    # for the datetime conversion month must be 2 digits
    if len(str(month_int)) == 1:
        month = "0" + str(month_int)
    else:
        month = str(month_int)
    # year is not given so either this or next year is assumed
    year = find_year(month_int)
    # convert to datetime obj
    date_str = str(year) + "-" + month + "-" + day + " " + time24
    datetime_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    datetime_obj = datetime_obj.replace(tzinfo=pytz.timezone(timezone))
    # convert to timezone given in config
    localized_datetime_obj = datetime_obj.astimezone(pytz.timezone(config.get_timezone()))

    return localized_datetime_obj


def convert_month(month):
    # converts month 3 character abbreviation to int
    month_lookup = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12
    }
    month_int = month_lookup.get(month, -1)
    if month_int == -1:
        logger.error("Can't find month " + month)
    return month_int


def find_year(month):
    # returns the year of the tournaments as int
    # this assumes if the number of the current month is higher than the number of the tournament,
    # the tournament must take place next year
    current_datetime = datetime.datetime.now()
    current_month = current_datetime.month
    if month < current_month:
        year = current_datetime.year + 1
    else:
        year = current_datetime.year
    return year


def find_link(name, host, driver):
    # uses the name and host of a tournament to search for it on its host_page
    # returns a DeepBattlefyTournament with the link
    base_url = "https://battlefy.com/"
    host_url = host.replace(" ", "-").lower()
    host_page = base_url + host_url
    driver.get(host_page)

    search_box = driver.find_element_by_xpath("//*[@id=\"org-hub\"]/div[2]/ui-view/bf-organization-tournaments/bf-org-tournament-list/div/div[1]/div/div[1]/bf-search-input/div/input")
    search_box.send_keys(name)
    search_box.send_keys(Keys.ENTER)
    time.sleep(1)
    link = extract_link(driver)
    return link


def extract_link(driver):
    # returns the full link to the tournament
    table = driver.find_element_by_css_selector('table')
    link = table.find_element_by_css_selector('a').get_attribute('href')
    return link
