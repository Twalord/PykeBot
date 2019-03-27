"""
Provides commands for the Discord Bot API. 🦆
:author: Jonathan Decker
"""
from utils import scrap_config as config
import logging
from discord.ext import commands
from battlefy.battlefy_scraper import scrape as scrape_battlefy
import asyncio
from concurrent.futures import ThreadPoolExecutor

"""
discord.py does not work with Python 3.7 to fix this:
in lib\site-packages\discord\compat.py line 32
needs to be changed to create_task = getattr(asyncio, 'async')
in lib\site-packages\websockets\compatibility.py line 9
needs to be changed to asyncio_ensure_future = getattr(asyncio, 'async')
in lib\site-packages\aiohttp\helpers.py line 25
needs to be changed to ensure_future = getattr(asyncio, 'async')
"""

logger = logging.getLogger('scrap_logger')
bot = commands.Bot(command_prefix="!")


def load_token():
    """
    Load the Bot Token from a file.
    A file called TOKEN must be provided containing only the token
    :return: String, the Bot Token
    """
    logger.debug("Trying to load Bot token")
    f = open("TOKEN", "r")
    token = ""
    token = f.readline()
    f.close()
    if len(token) > 0:
        logger.debug("Loaded Token.")
    else:
        logger.debug("No Token found.")
    return token


def run_bot():
    """
    Start the Bot
    :return: None
    """
    logger.info("Starting Discord Bot")
    token = load_token()
    bot.run(token)


def chunk_message(out_raw):
    """
    Messages in Discord are limited to 2000 characters so any bigger output needs to be chunked
    :param out_raw: String, the message that needs to be chunked
    :return: List[String], a list of Strings each with a length of 2000 characters
    """
    chunk_size = 2000
    out_list = [out_raw[i:i + chunk_size] for i in range(0, len(out_raw), chunk_size)]
    return out_list


@bot.event
async def on_ready():
    """
    Give a short report on starting up
    :return: None
    """
    logger.info('Logged in as')
    logger.info(bot.user.name)
    logger.info(bot.user.id)
    logger.info('------')


@bot.command(name='ping',
             description="test command response",
             brief="Pong!",
             aliases=["Ping"])
async def ping():
    """
    Ping test
    :return: None
    """
    await bot.say('Pong!')


@bot.group(name='scrape',
           description="Base command for webscraper selection",
           brief="Scrape <Website>",
           aliases=["Scrape", "Scr", "S"],
           pass_context=True)
async def base_scrape(ctx):
    if ctx.invoked_subcommand is None:
        await bot.say("Select a website to scrape by calling !scrape <Website>"
                      " (<Timeframe> <Filter>) for example !scrape Battlefy TODAY ARAM")

# TODO manage 0 tournaments found or left after filter case


@base_scrape.group(name='battlefy',
                   description="Surface scrape Battlefy for upcoming tournaments."
                               " A Timeframe can be added, available are TODAY, THIS_WEEK, THIS_WEEKEND",
                   brief="Scrape Battlefy",
                   aliases=["Battlefy", "Bat", "B"],
                   pass_context=True)
async def battlefy(ctx):
    if ctx.invoked_subcommand is battlefy:
        await bot.say("Starting Battlefy surface scraping based on settings \n"
                      "Timeframe: " + config.get_battlefy_time_frame() + "\n"
                                                                         "Filter: None")

        def sub_proc():
            return scrape_battlefy(time_frame=config.get_battlefy_time_frame())

        await run_battlefy_scraper(sub_proc)


@battlefy.group(name='today',
                description="Scrape Battlefy for upcoming tournaments today",
                brief="Scrape Battlefy Timeframe: Today",
                aliases=["TODAY", "Today", "t", "T"],
                pass_context=True)
async def battlefy_today(ctx, *args):
    if ctx.invoked_subcommand is battlefy_today:
        if len(args) > 0:
            await bot.say("Starting Battlefy surface scraping for time frame TODAY and " + args[0] + " as filter")
        else:
            await bot.say("Starting Battlefy surface scraping for time frame TODAY and no filter")

        def sub_proc():
            return scrape_battlefy(time_frame="TODAY")

        if len(args) > 0:
            await run_battlefy_scraper(sub_proc, args[0])
        else:
            await run_battlefy_scraper(sub_proc)


@base_scrape.group(name='battlefy_deep',
                   description="Surface scrape Battlefy for upcoming tournaments."
                               " A Timeframe can be added, available are TODAY, THIS_WEEK, THIS_WEEKEND",
                   brief="Deep Scrape Battlefy",
                   aliases=["Battlefy_deep", "Battlefy_Deep", "Bat_Deep", "Bat_D", "bat_deep", "B_D", "b_d", "bd"],
                   pass_context=True)
async def battlefy_deep(ctx):
    if ctx.invoked_subcommand is battlefy_deep:
        await bot.say("Starting Battlefy deep scraping based on settings \n"
                      "Timeframe: " + config.get_battlefy_time_frame() + "\n"
                                                                         "Filter: None")

        def sub_proc():
            return scrape_battlefy(time_frame=config.get_battlefy_time_frame(), scrape_deep=True)

        await run_battlefy_scraper(sub_proc)


@battlefy_deep.group()
async def battlefy_deep_today(ctx, *, arg):
    if ctx.invoked_subcommand is battlefy_deep_today:
        await bot.say("Starting Battlefy deep scraping for time frame TODAY and no Filter")

        def sub_proc():
            return scrape_battlefy(scrape_deep=True, time_frame="TODAY")

        await run_battlefy_scraper(sub_proc)


async def run_battlefy_scraper(func, filter_=""):
    loop = asyncio.get_event_loop()
    tournaments = await loop.run_in_executor(ThreadPoolExecutor(), func)
    if tournaments.filter_viable(filter_):
        tournaments = tournaments.filter_format(filter_)
    tournament_list = tournaments.tournaments
    out_raw = ""
    for tournament in tournament_list:
        out_raw += str(tournament) + "\n"
    out_list = chunk_message(out_raw)
    for out in out_list:
        await bot.say(out)


# ----------------------------------------------
"""
@bot.command(name='scrape Battlefy',
             description="scrape information on upcoming tournaments from the Battlefy website",
             brief="scrape Battlefy")


@bot.group(name='scrape_Battlefy'
           pass_context=True)
async def call_battlefy_scraper(ctx):
    if ctx.invoked_subcommand is None:
        await bot.say("Starting scrape with base settings")
        loop = asyncio.get_event_loop()

        def sub_proc():
            return scrape_battlefy()
        tournaments = await loop.run_in_executor(ThreadPoolExecutor, sub_proc)
        tournaments_list = tournaments.tournaments
        out_raw = ""
        for tournament in tournaments_list:
            out_raw += str(tournament) + "\n"
        out_list = chunk_message(out_raw)
        for out in out_list:
            await bot.say(out)


@call_battlefy_scraper.command()
async def deep():
    await bot.say("Starting deep scrape with base settings")
    loop = asyncio.get_event_loop()

    def sub_deep():
        return scrape_battlefy(scrape_deep=True)
    tournaments = await loop.run_in_executor(ThreadPoolExecutor(), sub_deep)
    tournaments_list = tournaments.tournaments
    out_raw = ""
    for tournament in tournaments_list:
        out_raw += str(tournament) + "\n"
    out_list = chunk_message(out_raw)
    for out in out_list:
        await bot.say(out)


@bot.command()
async def call_stalk_toornament(arg):
    logger.debug("Toornament stalker called by user")
    await bot.say("Starting toornament stalker")

    def sub_stalk_toornament():
        return stalk_toornament(arg)
    loop = asyncio.get_event_loop()
    multi_links = await loop.run_in_executor(ThreadPoolExecutor(), sub_stalk_toornament)
    out_raw = ""
    for link in multi_links:
        out_raw += link[0] + " " + link[1] + "\n"
    out_list = chunk_message(out_raw)
    for out in out_list:
        await bot.say(out)



@bot.command()
async def build_multi_link(ctx, *args):
    await bot.say(build_opgg_multi_link(args))
"""
