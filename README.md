# Steamgifts Bot

A simple bot that automatically joins giveaways on [steamgifts](steamgifts.com).
Not in any way affiliated.

## How to use
Simply log into your Steam account on steamgifts.com and export the cookies, then just paste the PHPSESSID value into the config.ini file. After that you are ready to start the bot! 

## config.ini
Before you will be able to use the bot, you have change some values in the config.ini file.  

The only line you HAVE to change is the first one. Just paste your PHPSESSID value after the `cookie =`, after that you are good to got, or you can adjust other things to your liking.
```
...
cookie = PASTE PHPSESSID COOKIE HERE
...
```
The next line defines how many points the bot should 'reserve', as in a minimum of points the bot can't undercut.
```
...
min_points = 1
...
```
When there are no more giveaways for the bot to check, it will try to wait for a specified amount of points until it refreshes and looks for new giveaways. `min_points_on_page_refresh` defines this value.
```
...
min_points_on_page_refresh = 6
...
```
Defines how many seconds the bot should wait until he refreshes the page.
```
...
refresh_sleep = 180
...
```
Defines how many pages deep the bot should check giveaways. 
```
...
number_of_pages = 5
...
```
Defines the minimum cost to join a giveaway, raise this value to avoid winning cheap/crappy games.
```
...
min_giveaway_cost = 1
...
```
The value `verbosity_level` defines the verbosity level for debugging purposes (1-4). 
```
...
verbosity_level = 1
...
```