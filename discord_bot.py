"""
Provides commands for the Discord Bot API. 🦆
:author: Jonathan Decker
"""
from utils import scrap_config as config
import logging
from discord.ext import commands
from stalkmaster import call_stalk_master
import asyncio
from concurrent.futures import ThreadPoolExecutor
from discord import Game
from utils.status_list import get_status
import os


"""
Requirements were updated, this fix should not be necessary anymore.
discord.py does not work with Python 3.7 to fix this:
in lib\site-packages\discord\compat.py line 32
needs to be changed to create_task = getattr(asyncio, 'async')
in lib\site-packages\websockets\compatibility.py line 9
needs to be changed to asyncio_ensure_future = getattr(asyncio, 'async')
in lib\site-packages\aiohttp\helpers.py line 25
needs to be changed to ensure_future = getattr(asyncio, 'async')
"""

logger = logging.getLogger('scrap_logger')
bot = commands.Bot(command_prefix=".lol")


class NoTokenFoundError(Exception):
    """
    Raised when no Discord Bot Token was found
    """
    logger.error("No Bot Token was found. The Discord Bot API Token needs to be placed in a file called TOKEN")


def load_token():
    """
    Load the Bot Token from a file.
    A file called TOKEN must be provided containing only the token
    :return: String, the Bot Token
    """
    logger.info("Trying to load Bot token")
    token = ""
    try:
        f = open("TOKEN", "r")
        token = f.readline()
        f.close()
    except FileNotFoundError:
        pass
    if len(token) > 0:
        logger.info("Loaded Token.")
    else:
        logger.info("No Token file found.")
        logger.info("Trying env variables.")
        token = os.environ['TOKEN']
        if len(token) > 0:
            logger.info("Loaded Token.")
        else:
            raise NoTokenFoundError
    return token.strip()


def run_bot():
    """
    Start the Bot
    :return: None
    """
    logger.info("Starting Discord Bot")
    try:
        token = load_token()
    except NoTokenFoundError:
        return
    bot.run(token)


def chunk_message(out_raw):
    """
    Messages in Discord are limited to 2000 characters so any bigger output needs to be chunked
    while respecting line breaks in the message
    :param out_raw: String, the message that needs to be chunked
    :return: List[String], a list of Strings each with a length of up to 2000 characters
    """
    chunk_size = 2000
    # out_list = [out_raw[i:i + chunk_size] for i in range(0, len(out_raw), chunk_size)]
    out_split = out_raw.split("\n")
    out_list = []
    message = ""
    for split in out_split:
        if len(message + split) > chunk_size:
            out_list.append(message)
            message = ""
        message += "\n" + split
    out_list.append(message)

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

    await update_client_presence(get_status())


@bot.command(name='ping',
             description="test command response",
             brief="Pong!",
             aliases=["Ping"],
             pass_context=True)
async def ping(ctx):
    """
    Ping test
    :return: None
    """
    await ctx.send('Pong!')


@bot.command(name='stalk',
             description="Gathers all player names and builds multilinks per team in the given link to a tournament or"
                         "match. Supported are Challengermode matches, Toornament tournaments, SINN League seasons,"
                         "groups and teams.",
             brief="stalk will return team names and multilinks for teams in the given tournament or match.",
             pass_context=True)
async def stalk(ctx, *args):
    logger.info("received user command scrape " + str(args))
    # prepare asyncio loop to avoid timeout
    loop = asyncio.get_event_loop()
    arg_list = list(args)
    if not len(arg_list) == 1:
        await ctx.send("Usage is .lolstalk url")
        return

    def sub_proc():
        return call_stalk_master(arg_list[0])

    # call taskmaster with args and is_scrape = True
    out_raw = await loop.run_in_executor(ThreadPoolExecutor(), sub_proc)

    # chunk und send results
    out_chunked = chunk_message(out_raw)
    for out in out_chunked:
        await ctx.send(out)


@bot.command(name='extstalk',
             description="Same as stalk but in addition the bot will look up the current soloQ ranking for each player"
                         "on op.gg and add it to the output. This might take longer.",
             brief="Same as stalk but also gathers player rankings.",
             pass_context=True)
async def ext_stalk(ctx, *args):
    logger.info("received user command scrape " + str(args))
    # prepare asyncio loop to avoid timeout
    loop = asyncio.get_event_loop()
    arg_list = list(args)
    if not len(arg_list) == 1:
        await ctx.send("Usage is .lolextstalk url")
        return

    def sub_proc():
        return call_stalk_master(arg_list[0], extendend=True)

    # call taskmaster with args and is_scrape = True
    out_raw = await loop.run_in_executor(ThreadPoolExecutor(), sub_proc)

    # chunk und send results
    out_chunked = chunk_message(out_raw)
    for out in out_chunked:
        await ctx.send(out)


async def update_client_presence(status: str):
    """
    Updates the bots presence to the given status, always with playing at front
    :param status: str, any valid string
    :return: None, but the bots presence was changed
    """
    await bot.change_presence(activity=Game(name=status))


@bot.command(name='setregion',
             description="Sets the region used for player lookups. The abbreviation format should be used so EUW for"
                         "Europe West, NA for North America and so on.",
             brief="Sets the region used for player lookups.",
             pass_context=True)
async def update_region(ctx, *args):
    logger.info("received user command scrape " + str(args))
    arg_list = list(args)
    if len(arg_list) == 1:
        config.set_region(arg_list[0])
        new_region = config.get_region()
        await ctx.send(f"Region setting has been changed to {new_region}")
    else:
        await ctx.send("Usage is .lolsetregion region")
