# League Tournament Stalker

<table>
    <tr>
        <td>Travis CI</td>
        <td><img src='https://travis-ci.org/Twalord/League_Tournament_Stalker.svg?branch=master'></td>
        <td>Coverage</td>
        <td><img src='https://codecov.io/gh/Twalord/League_Tournament_Stalker/branch/master/graph/badge.svg'></td>
    </tr>
</table>

This bot collects League of Legends summoner names for the participants of tournaments.
Given a link the bot will find all players in the tournament and build op.gg multilinks for them,
further the bot can go on op.gg and add soloQ rankings to each team and player.

For now the bot supports SINN League, Toornament and Challengermode.

## Installation

The required libraries can be installed via pip.
Simply run pip install -r requirements.txt in the project folder.

The geckodriver can be found here https://github.com/mozilla/geckodriver/releases
for windows user simply place the geckodriver.exe in the same folder as this project.
Firefox needs to be installed in order for this to work.

The bot also requires a valid Discord api token which needs to be placed in a file called TOKEN in project folder.

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

Challengermode Matches

Summoners INN League Seasons

Summoners INN League Groups

Summoners INN League Teams

Toornament Tournaments

## TODO

- finish challengermode tournament stalker
- add support for esl page stalking
