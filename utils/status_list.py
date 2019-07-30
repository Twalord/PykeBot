"""
🦆
:author: Jonathan Decker
"""
"""
import random

bots = "Alistar,Amumu,Annie,Ashe,Blitzcrank,Brand,Caitlyn,Cassiopeia,Cho\'Gath,Darius,Dr. Mundo,Ezreal,Fiddlesticks," \
       "Galio,Garen,Graves,Jax,Karthus,Kayle,Kog\'Maw,Leona,Lucian,Lux,Malphit,eMaster Yi,Miss Fortune,Morgana,Nasus," \
       "Nidalee,Rammus,Renekton,Ryze,Shen,Shyvana,Sivir,Soraka,Taric,Tristana,Trundle,Udyr,Warwick,Wukong,Veigar," \
       "Vladimir,Ziggs,Zilean,Zyra,Ahri,Jinx,Katarina,Nami,Nocturne,Olaf,Orianna,Sion,Teemo,Vayne," \
       "Volibear,Yasuo".split(",")


def get_random_bot():
    return random.choice(bots)

"""


def get_status():
    # bot = get_random_bot()
    # status = "as " + bot + " Bot"
    status = ".lolstalk <url>"
    return status
