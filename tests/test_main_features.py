"""
Contains integration tests for the main features

:author: Jonathan Decker
"""


def test_config():
    import os
    os.chdir("..")
    from utils import scrap_config as config
    region = "EUW"
    timezone = "CET"

    config.set_region(region)
    config.set_timezone(timezone)

    assert config.get_region() == region
    assert config.get_timezone() == timezone


def test_toornaments_stalker():
    from stalker.toornament_stalker import stalk
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
    pass

    # this feature is not ready yet

    #team_list = stalk_challengermode("https://www.challengermode.com/Tournaments/Show/30ddf5f5-5e59-e911-b49d-28187814ffef")

    # assert type(str(team_list)) == str
    # assert len(team_list.teams) > 0
    # assert isinstance(team_list, TeamList)


def test_sinn_league_stalker():
    from stalker import sinn_league_stalker
    from models import TeamList
    url = "https://www.summoners-inn.de/de/leagues/sinn/1338-season-3"
    team_lists = sinn_league_stalker.stalk(url)

    for team_list in team_lists.team_lists:
        assert type(str(team_list)) == str
        assert len(team_list.teams) > 0
        assert isinstance(team_list, TeamList)


def test_challengermode_quick_stalker():
    """
    Challengermode stalker needs to be updated to match redesigned website
    """
    return
    from stalker.challengermode_stalker import quick_stalk
    from models import TeamList
    team_list = quick_stalk("https://www.challengermode.com/Challenges/View/672fa046-3b77-e911-abc4-0003ffde309b")

    assert type(str(team_list)) == str
    assert len(team_list.teams) > 0
    assert isinstance(team_list, TeamList)


def test_stalkmaster():
    from stalkmaster import call_stalk_master
    urls = ["https://www.toornament.com/tournaments/2324026559405285376/information",
            # "https://www.challengermode.com/Challenges/View/672fa046-3b77-e911-abc4-0003ffde309b",
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