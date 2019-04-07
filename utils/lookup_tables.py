"""
Contains lookup tables for command aliases, needs to be updated upon adding new functions
:author: Jonathan Decker
"""
# define the lookup table, should be updated when adding functions
from battlefy.battlefy_scraper import scrape as battlefy_scrape, scrape_deep as battlefy_scrape_deep
from esl.esl import scrape as esl_scrape
from toornament.toornament_stalker import stalk as toornament_stalk

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
