# League Tournament Scraper

This bot collects information about upcoming League of Legends tournaments from the websites battlefy, ESL and challengermode.

Its goal is to give the user more overview on what tournaments are available by gathering information from different places
and providing filter to make sure only relevant information are displayed.

## Installation

The bot requires beautifulsoup4, selenium, pytz and the geckodriver.

Beatifulsoup4, pytz and selenium can be installed via pip.
Simply run pip install -r requirements.txt in the project folder.

The geckodriver can be found here https://github.com/mozilla/geckodriver/releases
for windows user simply place the geckodriver.exe in the same folder as this project.
Firefox needs to be installed in order for this to work.

## Usage

Running main.py will start the Discord Bot which will await commands.


## TODO

- implement scraping for ESL page
- implement scraping for challengermode
- implement scraping for toornament
- implement SINN League stalker

- extend scraping

- gather usage statistics