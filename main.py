"""
Main module for the League_Tournament_Scraper.

Only used for testing for now.
:author: Jonathan Decker
"""

from utils import scrap_config as config, scrap_logger
import time
start_time = time.perf_counter()

# setup logger
logger = scrap_logger.setup_logger()
logger.debug("Start of program")

run_tests = True
start_bot = False

tests = {"config": False,
         "battlefy_scrape": False,
         "toornament_stalker": False,
         "challengermode_stalker": False,
         "sinn_league_stalker": True}

# test config
if tests.get("config"):
    config.set_regions(["EUW"])
    config.set_battlefy_time_frame("TODAY")
    config.set_battlefy_url("https://battlefy.com/browse/league-of-legends?region=EU%20West&type=Any%20Format", "EUW")
    config.set_timezone("CET")
    config.set_websites(["ESL", "CHALLENGERMODE", "BATTLEFY"])


# test battlefy scrape
if tests.get("battlefy_scrape"):
    from battlefy.battlefy_scraper import scrape
    battlefy_tournaments = scrape(scrape_deep=True)
    filtered_tournaments = battlefy_tournaments.filter_format(form="ARAM")
    logger.debug("listing " + str(len(filtered_tournaments)) + " tournaments")
    print(str(filtered_tournaments))


# test toornament_stalker
if tests.get("toornament_stalker"):
    from toornament.toornament_stalker import stalk
    multi_links = stalk("https://www.toornament.com/tournaments/2324026559405285376/information")
    for link in multi_links:
        print(link)


# test challengermode_stalker
if tests.get("challengermode_stalker"):
    from challengermode.challengermode_stalker import stalk as stalk_challengermode
    stalk_challengermode("https://www.challengermode.com/Tournaments/Show/30ddf5f5-5e59-e911-b49d-28187814ffef")


# test sinn_league_stalker
if tests.get("sinn_league_stalker"):
    from sinn_league import sinn_league_stalker
    from utils import player_lookup
    url = "https://www.summoners-inn.de/de/leagues/sinn/1338-season-3"
    team_lists = sinn_league_stalker.stalk(url)
    player_lookup.add_list_team_list_ranks(team_lists)
    for team_list in team_lists:
        print(team_list)

# Run Discord Bot
if start_bot:
    from discord_bot import run_bot
    run_bot()

end_time = time.perf_counter()
run_time = round(end_time - start_time, 2)
logger.info(f"Finished execution in {run_time} secs")
