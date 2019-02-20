import scrap_logger
import scrap_config as config

# setup logger
logger = scrap_logger.setup_logger()
logger.debug("Start of program")

# config needs to be loaded before other modules are imported or their load config is executed first
from battlefy_scraper import scrape as battlefy_scrape
from ast import literal_eval

# test config
# logger.debug(config.blank_getter("GENERAL", "REGIONS"))
# logger.debug(config.blank_getter("GENERAL", "sdfsdfREGIONS"))

# test battlefy scrape
battlefy_tournaments = battlefy_scrape()
logger.debug("listing " + str(len(battlefy_tournaments)) + " tournaments")
for tournament in battlefy_tournaments:
    print(str(tournament))
    print("\n")
