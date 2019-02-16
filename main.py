import scrap_logger
import scrap_config
import models

# setup logger
logger = scrap_logger.setup_logger()
logger.debug("Start of program")

# load configs
config = scrap_config.load_config(delete_config=True)
logger.info(config['GENERAL']['REGIONS'])

# test models
battlefy_tournament = models.BattlefyTournament("Fight for something", "27.5", "12:00", "EUW", "1v9")
logger.info(str(battlefy_tournament))
