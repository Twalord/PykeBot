import scrap_logger
import scrap_config

# setup logger
logger = scrap_logger.setup_logger()
logger.debug("Start of program")

# load configs
config = scrap_config.load_config(delete_config=True)

# config needs to be loaded before other modules are imported or their load config is executed first
from battlefy_scraper import scrape as battlefy_scrape
from ast import literal_eval

logger.debug(literal_eval(config['GENERAL']['REGIONS']))


# test battlefy scrape
battlefy_tournaments = battlefy_scrape()
for tournament in battlefy_tournaments:
    print(str(tournament))
    print("\n")
# TODO add filters to battlefy tournaments
