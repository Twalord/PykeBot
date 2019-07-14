# League Tournament Stalker NO SELENIUM

[![Build Status](https://travis-ci.com/Twalord/League_Tournament_Stalker.svg?branch=master)](https://travis-ci.com/Twalord/League_Tournament_Stalker)

[![codecov](https://codecov.io/gh/Twalord/League_Tournament_Stalker/branch/master/graph/badge.svg)](https://codecov.io/gh/Twalord/League_Tournament_Stalker)

This bot collects League of Legends summoner names for the participants of tournaments.
Given a link the bot will find all players in the tournament and build op.gg multilinks for them.
Furthermore, the bot can go on op.gg and add soloQ rankings to each team and player.

This version of the bot only supports Toornament and rank lookups but does not require selenium

## Installation

The bot requires Python Version 3.7 or newer.
The required libraries can be installed via pip.
Simply run pip install -r requirements.txt in the project folder.

The bot also requires a valid Discord api token which needs to be placed in a file called TOKEN in the project folder.
A tutorial on how to create a Discord Bot and token can be found here:
https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token

## Usage

Running main.py will start the Discord Bot which will await commands.
Available commands are:

!stalk url

!extstalk url

!setregion region

"stalk" will return team names and multilinks for teams in the given tournament or match.
"extstalk" additionally collects the player soloQ rankings. This might take a moment longer to run.
"setregion" will update the region used in the multilinks and player lookups.

## Features

The following links can be stalked:

Toornament Tournaments

