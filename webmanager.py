from selenium import webdriver


def open_session():
    """
    Open a selenium web session in Firefox
    :return: webdriver, with an open session
    """

    # opens a web session and returns the webdriver
    driver = webdriver.Firefox()
    driver.implicitly_wait(30)

    return driver


def quit_session(driver: webdriver):
    driver.quit()
