from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List
import pytz
import scrap_config as config


# for the models dataclasses are used, this feature has been implemented in python 3.7


@dataclass
class Tournament:
    name: str
    date_time: datetime
    region: str
    ttype: str
    starts_in: timedelta = timedelta.max

    def __str__(self):
        return self.name + " " + self.ttype + " " + self.date_time.strftime("%m-%d %H:%M:%S") + " starts in " + str(
            self.starts_in)

    def __post_init__(self):
        self.starts_in = self.calculate_start_time()

    def calculate_start_time(self):
        delta = self.date_time - datetime.now().replace(tzinfo=pytz.timezone(config.get_timezone()))
        return delta


@dataclass
class BattlefyTournament(Tournament):
    # add Battlefy specific stuff
    host: str = "unknown"
    # possible formats are 'ARAM', '5v5', '1v1', '3v3', 'other', 'unset'
    format: str = 'unset'
    website: str = 'Battlefy'

    def __str__(self):
        d = {"days": self.starts_in.days}
        d["hours"], rem = divmod(self.starts_in.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        fmt = "{days} days {hours}:{minutes}:{seconds}"
        return self.format + " | starts in: " + fmt.format(**d) + " | " + self.date_time.strftime(
            "%m-%d %H:%M:%S") + " | " + self.name + " | "+ self.host

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
class BattlefyTournamentList:
    tournaments: List[BattlefyTournament]
    time_stamp: datetime = datetime.now().replace(tzinfo=pytz.timezone(config.get_timezone()))

    def __str__(self):
        output = ""
        for t in self.tournaments:
            output += str(t) + "\n"
        return output

    def get_tournament(self):
        return self.tournaments[-1]

    def pop_tournament(self):
        return self.tournaments.pop()

    def get_tournament_list(self):
        return self.tournaments

    def filter_format(self, form):
        # returns a filtered BattlefyTournamentList without modifying the original object
        filtered_tournaments = []
        for t in self.tournaments:
            if t.format == form:
                filtered_tournaments.append(t)
        return BattlefyTournamentList(tournaments=filtered_tournaments, time_stamp=self.time_stamp)

    def __len__(self):
        return len(self.tournaments)


@dataclass
class ESLTournament(Tournament):
    # add ESL specific stuff
    website: str = 'ESL'


@dataclass
class ChallengermodeTournament(Tournament):
    # add Challengermode specific stuff
    website: str = 'Challengermode'
