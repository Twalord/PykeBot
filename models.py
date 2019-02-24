from dataclasses import dataclass
from datetime import datetime
# for the models dataclasses are used, this feature has been implemented in python 3.7

@dataclass
class Tournament:
    name: str
    date_time: datetime
    region: str
    ttype: str

    def __str__(self):
        return self.name + " " + self.ttype + " " + self.date_time.strftime("%m-%d %H:%M:%S")


@dataclass
class BattlefyTournament(Tournament):
    # add Battlefy specific stuff
    host: str = "unknown"
    # possible formats are 'ARAM', '5v5', '1v1', '3v3', 'other', 'unset'
    format: str = 'unset'
    website: str = 'Battlefy'

    def __str__(self):
        return self.format + " | " + self.date_time.strftime("%m-%d %H:%M:%S") + " | " + self.name

    def __post_init__(self):
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
class ESLTournament(Tournament):
    # add ESL specific stuff
    website: str = 'ESL'


@dataclass
class ChallengermodeTournament(Tournament):
    # add Challengermode specific stuff
    website: str = 'Challengermode'
