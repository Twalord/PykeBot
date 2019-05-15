from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.add_argument("--headless")


def open_session(headless=True):
    """
    Open a selenium web session in Firefox
    :return: webdriver, with an open session
    """

    # opens a web session and returns the webdriver
    if headless:
        driver = webdriver.Firefox(options=options)
    else:
        driver = webdriver.Firefox()
    driver.implicitly_wait(30)

    return driver


def quit_session(driver: webdriver):
    driver.quit()
