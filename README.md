# PykeBot NO SELENIUM

![alt text](./PykeIconResize.jpg)

[![Build Status](https://travis-ci.com/Twalord/PykeBot.svg?branch=No_Selenium)](https://travis-ci.com/Twalord/PykeBot)
[![codecov](https://codecov.io/gh/Twalord/PykeBot/branch/No_Selenium/graph/badge.svg)](https://codecov.io/gh/Twalord/PykeBot)

PykeBot is a Discord bot that collects League of Legends summoner names for the participants of tournaments.
Given a link the bot will find all players in the tournament and build op.gg multilinks for them.
Furthermore, the bot can go on op.gg and add soloQ rankings to each team and player.

This version of PykeBot only supports Toornament, premiertour and rank lookups but does not require selenium
and was designed to be hosted on https://www.heroku.com/.

## Installation

This version is designed to be hosted on https://www.heroku.com/.
In order to do so you need accounts on heroku, github and discord.

1. Fork this project to your github account.
2. Go on your heroku account and create a new app.
3. Select Deploy and connect your github account.
4. Select the forked project with the no_selenium branch and deploy.
5. Create a discord bot and add it to your server, also keep the token. 
    Instructions for this step can be found here: https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token
6. On heroku go to settings and reveal config vars.
7. Add a new one with TOKEN as KEY and your discord bot token as VALUE.
8. Select Resources, one process 'main' should be visible.
9. Press on edit for it and switch it to on.
10. Done, the bot should now appear as online and react to commands in its dedicated channel.

## Usage

Available commands are:

.lolstalk url

.lolextstalk url

.lolsetregion region

"stalk" will return team names and multilinks for teams in the given tournament or match.
"extstalk" additionally collects the player soloQ rankings. This might take a moment longer to run.
"setregion" will update the region used in the multilinks and player lookups.

## Features

The following links can be stalked:

Toornament Tournaments

Premiertour Leagues
   
The link must be to the main page of the toornament.

## Credit
The PykeBot Icon was designed by the talented Binidi:
https://www.deviantart.com/binidi/art/Pyke-Icon-808245658