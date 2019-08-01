"""
Provides classes for the project.

:author: Jonathan Decker
"""

from dataclasses import dataclass
from typing import List
import logging
from utils import scrap_config as config

logger = logging.getLogger('scrap_logger')
# for the models dataclasses are used, this feature has been implemented in python 3.7


@dataclass
class Rank:
    """
    Saves a player rank as string and integer
    """
    string = ""
    rating = 0

    def __init__(self, rank_string, rating):
        self.string = rank_string
        self.rating = rating

    def __str__(self):
        return self.string


@dataclass
class Player:
    """
    Saves information on a single league account
    """
    summoner_name: str
    rank: Rank
    opgg: str = ""

    def __init__(self, sum_name, rank=None):
        self.summoner_name = sum_name
        self.rank = rank

    def __post_init__(self):
        region = config.get_region()
        base_url = "https://" + region + ".op.gg/summoner/userName="
        self.opgg = base_url + self.summoner_name.replace(" ", "")

    def __str__(self):
        if Rank is None:
            return self.summoner_name
        else:
            return f"{self.summoner_name} *{str(self.rank)}*"


@dataclass
class Team:
    """
    Saves information for a team of league players
    """
    name: str
    player_list: List[Player]
    multi_link: str = ""
    average_rank: Rank = None
    max_rank: Rank = None

    def build_opgg_multi_link(self):
        """
        construct a valid op.gg multi link for the given summoner names
        :return: String, url to the multilink for the given names
        """
        region = config.get_region()
        base_url = f"https://{region}.op.gg/multi/query="
        multi_link = base_url
        for player in self.player_list:
            multi_link += player.summoner_name.replace(" ", "")
            multi_link += "%2C"
        return multi_link

    def __post_init__(self):
        self.multi_link = self.build_opgg_multi_link()

    def __str__(self):
        if self.average_rank is None:
            return f"__{self.name}__ | {self.multi_link}"
        else:
            return f"__{self.name}__ Ø: {str(self.average_rank)} max: {str(self.max_rank)} | {self.multi_link}"

    def extended_str(self):
        out = str(self) + "\n"
        for player in self.player_list:
            out += str(player) + " | "
        return out[:-3]


@dataclass
class TeamList:
    """
    Saves a list of teams and the name of the list
    """
    name: str
    teams: List[Team]

    def __str__(self):
        out = f"__**{self.name}**__ \n"
        for team in self.teams:
            out += str(team) + "\n"
        return out

    def extended_str(self):
        out = f"__**{self.name}**__ \n"
        for team in self.teams:
            out += team.extended_str() + "\n"
        return out


@dataclass
class TeamListList:
    """
    Saves a list of TeamList objects
    """
    team_lists: List[TeamList]

    def __str__(self):
        out = ""
        for team_list in self.team_lists:
            out += str(team_list)
        return out

    def extended_str(self):
        out = ""
        for team_list in self.team_lists:
            out += team_list.extended_str()
        return out