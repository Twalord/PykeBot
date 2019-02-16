import scrap_logger
import scrap_config

logger = scrap_logger.setup_logger()
logger.debug("Start of program")
config = scrap_config.load_config(delete_config=True)
logger.info(config['GENERAL']['REGIONS'])
