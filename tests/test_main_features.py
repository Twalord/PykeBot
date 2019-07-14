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


def test_stalkmaster():
    from stalkmaster import call_stalk_master
    urls = ["https://www.toornament.com/tournaments/2324026559405285376/information"]
    for url in urls:
        out = call_stalk_master(url)
        assert type(out) == str
        assert len(out) > 0

    out = call_stalk_master(urls[0], True)
    assert type(out) == str
    assert len(out) > 0
