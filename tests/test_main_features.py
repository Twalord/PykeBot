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

    for team_list in team_lists.team_lists:
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


def test_stalkmaster():
    from stalkmaster import call_stalk_master
    urls = ["https://www.toornament.com/tournaments/2324026559405285376/information",
            "https://www.challengermode.com/Challenges/View/672fa046-3b77-e911-abc4-0003ffde309b",
            "https://www.summoners-inn.de/de/leagues/sinn/1338-season-3/group/209-gruppenphase/5055-division-1-1",
            "https://www.summoners-inn.de/de/leagues/sinn/1338-season-3/group/209-gruppenphase/3452-gruppe-3-2",
            "https://www.summoners-inn.de/de/leagues/sinn/1338-season-3/teams/94634-unicorns-of-love",
            "https://www.summoners-inn.de/de/leagues/sinn/1338-season-3"]
    for url in urls:
        out = call_stalk_master(url)
        assert type(out) == str
        assert len(out) > 0

    out = call_stalk_master(urls[0], True)
    assert type(out) == str
    assert len(out) > 0