"""
Main module for the League_Tournament_Stalker.

Only used for testing for now.
:author: Jonathan Decker
"""

from utils import scrap_logger
import time
start_time = time.perf_counter()

# setup logger
logger = scrap_logger.setup_logger()
logger.debug("Start of program")

# Run Discord Bot
from discord_bot import run_bot
run_bot()

end_time = time.perf_counter()
run_time = round(end_time - start_time, 2)
logger.info(f"Finished execution in {run_time} secs")
