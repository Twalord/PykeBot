"""
Provides classes for the project.

:author: Jonathan Decker
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List
import pytz
from utils import scrap_config as config
import logging
from itertools import combinations

logger = logging.getLogger('scrap_logger')
# for the models dataclasses are used, this feature has been implemented in python 3.7


@dataclass
class Tournament:
    """
    Base-class for all tournaments
    """

    name: str
    date_time: datetime
    region: str
    ttype: str
    website: str
    starts_in: timedelta = timedelta.max
    # possible formats are 'ARAM', '5v5', '1v1', '3v3', 'other', 'unset'
    format: str = 'unset'

    def __str__(self):
        return self.name + " " + self.ttype + " " + self.date_time.strftime("%m-%d %H:%M:%S") + " starts in " + str(
            self.starts_in)

    def __eq__(self, other):
        if isinstance(other, Tournament):
            if self.name == other.name and self.date_time == other.date_time:
                return True
        return False

    def __post_init__(self):
        self.starts_in = self.calculate_start_time()

    def calculate_start_time(self):
        delta = self.date_time - datetime.now().replace(tzinfo=pytz.timezone(config.get_timezone()))
        return delta


@dataclass
class BattlefyTournament(Tournament):
    """
    Saves and handles Battlefy tournaments.
    """

    # add Battlefy specific stuff
    host: str = "unknown"
    website: str = 'Battlefy'

    def __str__(self):
        d = {"days": self.starts_in.days}
        d["hours"], rem = divmod(self.starts_in.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        fmt = "{days} days {hours}:{minutes}:{seconds}"
        return self.format + " | starts in: " + fmt.format(**d) + " | " + self.date_time.strftime(
            "%m-%d %H:%M:%S") + " | " + self.name + " | " + self.host

    def __post_init__(self):
        super().__post_init__()
        self.format = self.determine_format()

    def determine_format(self):
        # extracts the tournament format from the name
        name_list = self.name.replace("[", " ").replace("]", " ").lower().split()
        if self.ttype == "1v1":
            return "1v1"
        elif 'aram' in name_list:
            return "ARAM"
        elif 'twisted' and 'treeline' in name_list:
            return "3v3"
        elif ('5' and ('v' or 'vs')) or '5v5' or '5vs5' in name_list:
            return "5v5"
        else:
            return "other"


@dataclass
class DeepBattlefyTournament(BattlefyTournament):
    """
    Saves additional Battlefy information acquired by a deeper search.
    """

    # saves additional information like the link
    link: str = ""
    # teams_count: int = -1
    # players_count: int = -1

    def __str__(self):
        return super().__str__() + " | " + self.link


@dataclass
class TournamentList:
    """
    Saves a List of Tournament objects allowing operations on all tournaments in the list
    """
    tournaments: List[Tournament]
    time_stamp: datetime = datetime.now().replace(tzinfo=pytz.timezone(config.get_timezone()))

    def __str__(self):
        output = ""
        for t in self.tournaments:
            output += str(t) + "\n"
        return output

    def __len__(self):
        return len(self.tournaments)

    def get_tournament(self):
        """
        Returns the last tournament in the list.
        :return: Tournament
        """

        return self.tournaments[-1]

    def pop_tournament(self):
        """
        Returns the last tournament in the list and removes it.
        :return: Tournament
        """

        return self.tournaments.pop()

    def get_tournament_list(self):
        """
        Returns the list of BattlefyTournaments
        :return: List[Tournament]
        """

        return self.tournaments

    def append_tournament(self, new_tournament):
        """
        Adds the given tournament to the list.
        :param new_tournament: Tournament, or any inheriting class
        :return: None, but the list was modified
        """

        if isinstance(new_tournament, Tournament):
            self.tournaments.append(new_tournament)
        else:
            logger.debug("Can't append object to TournamentList as it is no Tournament object")
            logger.debug(str(new_tournament))

    def append_tournaments(self, new_tournaments):
        """
        Adds the given tournaments to the list.
        :param new_tournaments: List[Tournament]
        :return: None, but the list was modified
        """

        for new_tournament in new_tournaments:
            self.append_tournament(new_tournament)

    def remove_duplicates(self):
        """
        Removes all duplicates from the list
        :return: None, but the list was modified
        """

        for tournament, other_tournament in combinations(self.tournaments, 2):
            if tournament.__eq__(other_tournament):
                self.tournaments.remove(other_tournament)

    @staticmethod
    def filter_viable(test_filter):
        """
        Tests if the filter is viable
        :param test_filter: String, must be "1v1", "3v3", "5v5", "ARAM", "other" to be viable
        :return: Boolean, True if the filter is viable
        """
        viable_filter = ["1v1", "3v3", "5v5", "ARAM", "other"]
        if test_filter in viable_filter:
            return True
        else:
            return False

    def filter_format(self, form):
        """
        Returns a TournamentList object only containing the given format
        :param form: String, a valid format, valid formats are: "1v1", "3v3", "5v5", "ARAM", "other"
        :return: TournamentList
        """

        # returns a filtered TournamentList without modifying the original object
        filtered_tournaments = []
        for t in self.tournaments:
            if t.format == form:
                filtered_tournaments.append(t)
        return TournamentList(tournaments=filtered_tournaments, time_stamp=self.time_stamp)

    def merge_tournament_lists(self, other):
        """
        Adds anothers given TournamentList objects tournament list to this TournamentList and calls remove_duplicates
        :param other: TournamentList
        :return: None, but the tournaments list was modified
        """
        if isinstance(other, TournamentList):
            for tournament in other.tournaments:
                self.append_tournament(tournament)
            self.remove_duplicates()
        else:
            raise TypeError


@dataclass
class ESLTournament(Tournament):
    """
    Saves and handles ESL tournaments.
    """

    # add ESL specific stuff
    website: str = 'ESL'


@dataclass
class ChallengermodeTournament(Tournament):
    """
    Saves and handles Challengermode tournaments.
    """

    # add Challengermode specific stuff
    website: str = 'Challengermode'


@dataclass
class ToornamentTournament(Tournament):
    """
    Saves and handles Toornament tournaments.
    """
    website: str = 'Toornament'
