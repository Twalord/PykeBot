import scrap_config as config
import logging
from discord.ext import commands
from battlefy_scraper import scrape as scrape_battlefy
from toornament_stalker import stalk_toornament, build_opgg_multi_link
# discord.py does not work with Python 3.7 to fix this:
# in lib\site-packages\discord\compat.py line 32
# needs to be changed to create_task = getattr(asyncio, 'async')
# in lib\site-packages\websockets\compatibility.py line 9
# needs to be changed to asyncio_ensure_future = getattr(asyncio, 'async')
# in lib\site-packages\aiohttp\helpers.py line 25
# needs to be changed to ensure_future = getattr(asyncio, 'async')

logger = logging.getLogger('scrap_logger')

# Place the bot token in a file called TOKEN
logger.debug("Trying to load Bot token")
f = open("TOKEN", "r")
TOKEN = ""
TOKEN = f.readline()
f.close()
if len(TOKEN) > 0:
    logger.debug("Loaded Token.")
else:
    logger.debug("No Token found.")

bot = commands.Bot(command_prefix="!")


def run_bot():
    logger.info("Starting Discord Bot")
    bot.run(TOKEN)


@bot.event
async def on_ready():
    logger.info('Logged in as')
    logger.info(bot.user.name)
    logger.info(bot.user.id)
    logger.info('------')


@bot.command()
async def ping():
    await bot.say('Pong!')


@bot.command(name='scrape_Battlefy',
             description="scrape information on upcoming tournaments from the Battlefy website",
             brief="scrape Battlefy")
async def call_battlefy_scraper():
    logger.debug("Battlefy scraper called by user")
    await bot.say('Starting Scrape')
    tournaments = scrape_battlefy()
    tournaments_list = tournaments.tournaments
    out_raw = ""
    for tournament in tournaments_list:
       out_raw += str(tournament) + "\n"
    out_list = chunk_message(out_raw)
    for out in out_list:
        await bot.say(out)


@bot.command()
async def stalk_toornament(ctx, *args):
    logger.debug("Toornament stalker called by user")
    for arg in args:
        multi_links = stalk_toornament(arg)
        out_raw = ""
        for link in multi_links:
            out_raw += str(link) + "\n"
        out_list = chunk_message(out_raw)
        for out in out_list:
            await bot.say(out)


def chunk_message(out_raw):
    # messages are limited to 2000 characters so the output needs to be chunked
    n = 2000
    out_list = [out_raw[i:i+n] for i in range(0, len(out_raw), n)]
    return out_list


@bot.command()
async def build_multi_link(ctx, *args):
    await bot.say(build_opgg_multi_link(args))


@bot.command()
async def stalk_toornament_test(ctx, arg):
    await bot.say(str(stalk_toornament(arg)))

# KNOWN ERRORS:
# first argument passed is ignored
# calling stalk_toornament(arg) raises TypeError 'Command' object is not callable