import bs4
import logging
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException
import time

# Setup logger
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')
logging.debug('Start of program')

battlefy_url = "https://battlefy.com/browse/league-of-legends?region=EU%20West&type=Any%20Format"

driver = webdriver.Firefox()
driver.implicitly_wait(30)
logging.debug("opening: " + battlefy_url)
driver.get(battlefy_url)

# Presses the Load more Button until all tournaments for the time frame are on the page
while True:
    try:
        load_more_button = driver.find_element_by_xpath("//*[@id=\"ng-app\"]/body/bf-app/main/div/div/bf-browse/div/bf-tournament-card-list/div[2]/button")
        #time.sleep(2)
        load_more_button.click()
        time.sleep(2)

    except NoSuchElementException:
        break
    except ElementNotInteractableException:
        break
    # Handles the annoying popup by closing it
    except ElementClickInterceptedException:
        driver.switch_to.frame("intercom-modal-frame")
        close_button = driver.find_element_by_xpath("/html/body/div/div/span/div/div/div[2]/div/div/div/span")
        time.sleep(2)
        close_button.click()
        driver.switch_to.default_content()
        continue

battlefy_soup = bs4.BeautifulSoup(driver.page_source, features="html.parser")

tournament_container = battlefy_soup.find_all('div', class_="card-details")

driver.quit()

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

    print("\n")
    print("Name: " + name)
    print("Date: " + date)
    print("Time: " + time)
    print("Type: " + ttype)

print("\n")
logging.debug("A total of " + str(len(tournament_container)) + " tournaments were found.")
