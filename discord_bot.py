"""
Provides commands for the Discord Bot API. 🦆
:author: Jonathan Decker
"""
from utils import scrap_config as config
import logging
from discord.ext import commands
from discord.ext import tasks
from stalkmaster import call_stalk_master
import asyncio
from concurrent.futures import ThreadPoolExecutor
from discord import Game
from utils.status_list import get_status
import os
import pathlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime

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


class UsageReporter(commands.Cog):
    """
    provides recoding of bot usage, written to a txt file
    """

    def __init__(self, client):
        """
        Initiates the stats.txt file and starts the loop.
        :param bot: The Bot instance used for the Discord Bot.
        """
        self.bot = client

        self.path_to_stats = pathlib.Path.cwd() / "stats.txt"

        # checks if a file called stats.txt exists and if not creates it
        if not (self.path_to_stats.exists() and self.path_to_stats.is_file()):
            logger.info("Stats file not found, recreating.")
            f = open(str(self.path_to_stats), "w+")
            f.close()
        else:
            logger.info("Stats file found.")

        # adds these lines if they don't already exist
        s = open(str(self.path_to_stats)).read()
        if "server_count:" not in s:
            s += "\nserver_count:"
        if "server_names:" not in s:
            s += "\nserver_names:"
        if "stalk_call_count:" not in s:
            s += "\nstalk_call_count:"
        if "ext_call_count:" not in s:
            s += "\next_call_count:"

        f = open(str(self.path_to_stats), "w")
        f.write(s)
        f.close()

    def count_up(self, counter_name):
        """
        Opens the stats.txt file and counts the given counter up by one
        :param counter_name: str, must match one of the counter names in stats.txt
        :return: None
        """
        s = open(str(self.path_to_stats)).read()
        s_list = s.split("\n")
        for index, item in enumerate(s_list):
            if counter_name in item:
                only_counter_name, count = item.split(" ")
                count = str(int(count) + 1)
                s_list[index] = f"{only_counter_name} {count}"

        s_out = "\n".join(s_list)
        f = open(str(self.path_to_stats), "w")
        f.write(s_out)
        f.close()

    def cog_unload(self):
        self.run_loop.cancel()

    async def start(self):
        """
        initiates the stats and starts the loop
        :return: None
        """
        await self.bot.wait_until_ready()
        self.update_server_stats()

        self.run_loop.start()

    def update_server_stats(self):
        s = open(str(self.path_to_stats)).read()
        server_list = []
        for server in self.bot.guilds:
            server_list.append(server.name)
        server_list_string = ', '.join(server_list)
        s_list = s.split("\n")
        remove_in = []
        for index, item in enumerate(s_list):
            if "server_names:" in item:
                s_list[index] = "server_names: " + server_list_string
            if "server_count:" in item:
                s_list[index] = "server_count: " + str(len(server_list))
            if "stalk_call_count:" in item:
                s_list[index] = "stalk_call_count: 0"
            if "ext_call_count:" in item:
                s_list[index] = "ext_call_count: 0"
            if len(item) == 0:
                remove_in.append(index)

        for index in remove_in:
            s_list.remove(s_list[index])

        s_out = "\n".join(s_list)
        f = open(str(self.path_to_stats), "w")
        f.write(s_out)
        f.close()

    @tasks.loop(hours=24.0)
    async def run_loop(self):
        await self.upload()

    async def upload(self):
        pass
        # refresh server_names and server_count and add it to the file
        self.update_server_stats()

        # mail address is saved via env var or file
        logger.debug("Trying to load stats mail info")
        address = ""
        pw = ""
        try:
            f = open("MAIL", "r")
            address = f.readline()
            pw = f.readline()
            f.close()
        except FileNotFoundError:
            pass
        if len(address) > 0 and len(pw) > 0:
            logger.debug("Loaded Mail info.")
        else:
            logger.debug("No Mail file found.")
            logger.debug("Trying env variables.")
            address = os.environ['MAIL_ADD']
            pw = os.environ['MAIL_PW']
            if len(address) > 0 and len(pw) > 0:
                logger.debug("Loaded Mail Info.")
            else:
                bot.bg_task.cog_unload()
                logger.error("No Mail Info Found. To receive usage stats, add a file called MAIL"
                             " with address in the first line and password in the second")
                raise NoMailInfoFoundError

        address = address.strip()
        pw = pw.strip()

        # send the file per email to me
        content = open(str(self.path_to_stats)).read()

        # TODO only works for outlook, should be able to adapt to others
        mail_server = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
        mail_server.starttls()
        mail_server.login(address, pw)

        msg = MIMEMultipart()

        msg['From'] = address
        msg['To'] = address
        msg['Subject'] = f"Usage Report {str(datetime.datetime.now())}"

        msg.attach(MIMEText(content, 'plain'))

        logger.info(f"Sending usage report to {address}")
        mail_server.send_message(msg)

        del msg
        mail_server.quit()

    @run_loop.after_loop
    async def on_cancel(self):
        if self.run_loop.is_being_cancelled():
            await self.upload()


class MyBot(commands.Bot):
    """
    the UsageReporter needs to be saves as part of the bot to access its functions from everywhere
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, command_prefix=".lol")
        # self.bg_task = UsageReporter(self)


logger = logging.getLogger('scrap_logger')
bot = MyBot()


class NoTokenFoundError(Exception):
    """
    Raised when no Discord Bot Token was found
    """


class NoMailInfoFoundError(Exception):
    """
    Raised when no Mail info for the usage stats could be found.
    """


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
            logger.error("No Bot Token was found. The Discord Bot API Token needs to be placed in a file called TOKEN")
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
        logger.error("No Bot Token was found. The Discord Bot API Token needs to be placed in a file called TOKEN")
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

    await bot.bg_task.start()
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

    bot.bg_task.count_up("stalk_call_count:")

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

    bot.bg_task.count_up("ext_call_count:")

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
