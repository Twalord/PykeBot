
class Tournament:
    def __init__(self, name, date_time, region, ttype):
        self.name = name
        self.date_time = date_time
        self.region = region
        self.ttype = ttype

    def __str__(self):
        return self.name + " " + self.ttype + " " + self.date_time.strftime("%m-%d %H:%M:%S")


class BattlefyTournament(Tournament):
    # add Battlefy specific stuff
    def __init__(self, name, date_time, region, ttype):
        super().__init__(name, date_time, region, ttype)
        self.website = 'Battlefy'


class ESLTournament(Tournament):
    # add ESL specific stuff
    def __init__(self, name, date_time, region, ttype):
        super().__init__(name, date_time, region, ttype)
        self.website = 'ESL'


class ChallengermodeTournament(Tournament):
    # add Challengermode specific stuff
    def __init__(self, name, date_time, region, ttype):
        super().__init__(name, date_time, region, ttype)
        self.website = 'Challengermode'
