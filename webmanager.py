from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.add_argument("--headless")


def open_session():
    """
    Open a selenium web session in Firefox
    :return: webdriver, with an open session
    """

    # opens a web session and returns the webdriver
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(30)

    return driver


def quit_session(driver: webdriver):
    driver.quit()
