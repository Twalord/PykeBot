"""
Contains integration tests for the main features

:author: Jonathan Decker
"""
def test_config():
    import os
    os.chdir("..")
    from utils import scrap_config as config
    regions = ["EUW"]
    battlefy_time_frame = "TODAY"
    battlefy_url = ("https://battlefy.com/browse/league-of-legends?region=EU%20West&type=Any%20Format", "EUW")
    timezone = "CET"
    websites = ["ESL", "CHALLENGERMODE", "BATTLEFY"]

    config.set_regions(regions)
    config.set_battlefy_time_frame(battlefy_time_frame)
    config.set_battlefy_url(*battlefy_url)
    config.set_timezone(timezone)
    config.set_websites(websites)

    assert config.get_regions() == regions
    assert config.get_battlefy_time_frame() == battlefy_time_frame
    assert config.get_battlefy_url(battlefy_url[1]) == battlefy_url[0]
    assert config.get_timezone() == timezone
    assert config.get_websites() == websites


def test_normal_battlefy_scrape():
    from battlefy.battlefy_scraper import scrape
    from models import TournamentList
    battlefy_tournaments = scrape()
    filtered_tournaments = battlefy_tournaments.filter_format(form="ARAM")

    assert len(filtered_tournaments) > 0
    assert isinstance(filtered_tournaments, TournamentList)


def test_toornaments_stalker():
    from toornament.toornament_stalker import stalk
    from utils import player_lookup
    from models import TeamList

    team_list = stalk("https://www.toornament.com/tournaments/2324026559405285376/information")

    assert type(str(team_list)) == str
    assert len(team_list.teams) > 0
    assert isinstance(team_list, TeamList)

    player_lookup.add_team_list_ranks(team_list)

    for team in team_list.teams:
        for player in team.player_list:
            assert player.rank is not None


def test_challengermode_stalker():
    from challengermode.challengermode_stalker import stalk as stalk_challengermode
    from models import TeamList
    team_list = stalk_challengermode("https://www.challengermode.com/Tournaments/Show/30ddf5f5-5e59-e911-b49d-28187814ffef")

    assert type(str(team_list)) == str
    assert len(team_list.teams) > 0
    assert isinstance(team_list, TeamList)


def test_sinn_league_stalker():
    from sinn_league import sinn_league_stalker
    from models import TeamList
    url = "https://www.summoners-inn.de/de/leagues/sinn/1338-season-3"
    team_lists = sinn_league_stalker.stalk(url)

    for team_list in team_lists:
        assert type(str(team_list)) == str
        assert len(team_list.teams) > 0
        assert isinstance(team_list, TeamList)


def test_challengermode_quick_stalker():
    from challengermode.challengermode_stalker import quick_stalk
    from models import TeamList
    team_list = quick_stalk("https://www.challengermode.com/Challenges/View/672fa046-3b77-e911-abc4-0003ffde309b")

    assert type(str(team_list)) == str
    assert len(team_list.teams) > 0
    assert isinstance(team_list, TeamList)
