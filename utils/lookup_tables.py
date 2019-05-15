"""
Contains lookup tables for various modules
:author: Jonathan Decker
"""
# define the lookup table, should be updated when adding functions
from battlefy.battlefy_scraper import scrape as battlefy_scrape, scrape_deep as battlefy_scrape_deep
from esl.esl import scrape as esl_scrape
from toornament.toornament_stalker import stalk as toornament_stalk

"""
lookup tables for taskmaster to understand user commands
"""
b = "battlefy"
bd = "battlefy_deep"
e = "esl"
to = "toornament"
c = "challengermode"
call_list = [b, bd, e, to, c]
t = "TODAY"
w = "THIS WEEK"
we = "THIS WEEKEND"
time_frame_list = [t, w, we]
fiveVfive = "5v5"
threeVthree = "3v3"
oneVone = "1v1"
aram = "ARAM"
filter_list = [fiveVfive, threeVthree, oneVone, aram]
time_frame_lookup = {
    "today": t,
    "t": t,
    "w": w,
    "week": w,
    "this_week": w,
    "we": we,
    "weekend": we,
    "this_weekend": we
}
filter_lookup = {
    "5v5": fiveVfive,
    "3v3": threeVthree,
    "1v1": oneVone,
    "aram": aram
}
scrape_lookup = {
    "battlefy": b,
    "bat": b,
    "b": b,
    "battlefy_deep": bd,
    "bat_deep": bd,
    "bat_d": bd,
    "b_d": bd,
    "bd": bd,
    "esl": e,
    "e": e,
    "toornament": to,
    "to": to,
    "toor": to,
    "challengermode": c,
    "chal": c,
    "c": c,
    "challenger": c
}
stalk_lookup = {
    "toornament": to,
    "to": to,
    "toor": to
}
scrape_task_lookup = {
    b: battlefy_scrape,
    bd: battlefy_scrape_deep,
    e: esl_scrape
}
stalk_task_lookup = {
    to: toornament_stalk
}
"""
lookup tables for player_lookup to understand player rankings
"""
rank_lookup = {"unranked": 0,
               "iron iv": 1,
               "iron 4": 1,
               "iron iii": 2,
               "iron 3": 2,
               "iron ii": 3,
               "iron 2": 3,
               "iron i": 4,
               "iron 1": 4,
               "bronze iv": 5,
               "bronze 4": 5,
               "bronze iii": 6,
               "bronze 3": 6,
               "bronze ii": 7,
               "bronze 2": 8,
               "bronze i": 8,
               "bronze 1": 8,
               "silver iv": 9,
               "silver 4": 9,
               "silver iii": 10,
               "silver 3": 10,
               "silver ii": 11,
               "silver 2": 11,
               "silver i": 12,
               "silver 1": 12,
               "gold iv": 13,
               "gold 4": 13,
               "gold iii": 14,
               "gold 3": 14,
               "gold ii": 15,
               "gold 2": 15,
               "gold i": 16,
               "gold 1": 16,
               "platinum iv": 17,
               "platinum 4": 17,
               "platinum iii": 18,
               "platinum 3": 18,
               "platinum ii": 19,
               "platinum 2": 19,
               "platinum i": 20,
               "platinum 1": 20,
               "diamond iv": 21,
               "diamond 4": 21,
               "diamond iii": 22,
               "diamond 3": 22,
               "diamond ii": 23,
               "diamond 2": 23,
               "diamond i": 24,
               "diamond 1": 24,
               "master": 25,
               "master 1": 25,
               "master i": 25,
               "grandmaster": 26,
               "grandmaster 1": 26,
               "grandmaster i": 26,
               "challenger": 27,
               "challenger 1": 27,
               "challenger i": 27}

rating_lookup = {0: "Unranked",
                 1: "Iron 4",
                 2: "Iron 3",
                 3: "Iron 2",
                 4: "Iron 1",
                 5: "Bronze 4",
                 6: "Bronze 3",
                 7: "Bronze 2",
                 8: "Bronze 1",
                 9: "Silver 4",
                 10: "Silver 3",
                 11: "Silver 2",
                 12: "Silver 1",
                 13: "Gold 4",
                 14: "Gold 3",
                 15: "Gold 2",
                 16: "Gold 1",
                 17: "Platinum 4",
                 18: "Platinum 3",
                 19: "Platinum 2",
                 20: "Platinum 1",
                 21: "Diamond 4",
                 22: "Diamond 3",
                 23: "Diamond 2",
                 24: "Diamond 1",
                 25: "Master",
                 26: "Grandmaster",
                 27: "Challenger"}
