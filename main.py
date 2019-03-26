"""
Main module for the League_Tournament_Scraper.

Only used for testing for now.
:author: Jonathan Decker
"""

import scrap_logger
import scrap_config as config

# setup logger
logger = scrap_logger.setup_logger()
logger.debug("Start of program")

# config needs to be loaded before other modules are imported or their load config is executed first
from battlefy_scraper import scrape as battlefy_scrape
from toornament_stalker import stalk_toornament
from discord_interface import run_bot

# test config

config.set_regions(["EUW"])
config.set_battlefy_time_frame("TODAY")
config.set_battlefy_url("https://battlefy.com/browse/league-of-legends?region=EU%20West&type=Any%20Format", "EUW")
config.set_timezone("CET")
config.set_websites(["ESL", "CHALLENGERMODE", "BATTLEFY"])


# test battlefy scrape
"""
battlefy_tournaments = battlefy_scrape(scrape_deep=True)
filtered_tournaments = battlefy_tournaments.filter_format(form="ARAM")
logger.debug("listing " + str(len(filtered_tournaments)) + " tournaments")
print(str(filtered_tournaments))
"""

# test toornament_stalker
"""
multi_links = stalk_toornament("https://www.toornament.com/tournaments/2260729467409637376/information")
for link in multi_links:
    print(link)
"""

# test discord_interface
run_bot()
