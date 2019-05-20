"""
Main module for the League_Tournament_Stalker.

Only used for testing for now.
:author: Jonathan Decker
"""

from utils import scrap_config as config, scrap_logger
import time
start_time = time.perf_counter()

# setup logger
logger = scrap_logger.setup_logger()
logger.debug("Start of program")

start_bot = True

tests = {"config": False,
         "toornament_stalker": False,
         "challengermode_stalker": False,
         "sinn_league_stalker": False,
         "challengermode_quick_stalker": False}

# test config
if tests.get("config"):
    config.set_regions(["EUW"])
    config.set_battlefy_time_frame("TODAY")
    config.set_battlefy_url("https://battlefy.com/browse/league-of-legends?region=EU%20West&type=Any%20Format", "EUW")
    config.set_timezone("CET")
    config.set_websites(["ESL", "CHALLENGERMODE", "BATTLEFY"])


# test toornament_stalker
if tests.get("toornament_stalker"):
    from toornament.toornament_stalker import stalk
    from utils import player_lookup
    team_list = stalk("https://www.toornament.com/tournaments/2324026559405285376/information")
    player_lookup.add_team_list_ranks(team_list)
    print(str(team_list))


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


# test challengermode quick stalker
if tests.get("challengermode_quick_stalker"):
    from challengermode.challengermode_stalker import quick_stalk
    from utils import player_lookup
    team_list =quick_stalk("https://www.challengermode.com/Challenges/View/672fa046-3b77-e911-abc4-0003ffde309b")
    player_lookup.add_team_list_ranks(team_list)
    print(team_list.extended_str())

# Run Discord Bot
if start_bot:
    from discord_bot import run_bot
    run_bot()

end_time = time.perf_counter()
run_time = round(end_time - start_time, 2)
logger.info(f"Finished execution in {run_time} secs")
