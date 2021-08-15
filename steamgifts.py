import sys
import configparser
import json
import datetime
import os
from time import sleep
from random import randint
from requests import RequestException
from bs4 import BeautifulSoup
import requests

CONFIG_DEFAULT = {
    'cookie': 'COPY PHPSESSID HERE',
    'min_points': 1,
    'min_points_on_page_refresh': 6,
    'refresh_sleep': 180,
    'number_of_pages': 5,
    'min_giveaway_cost': 1,
    'verbosity_level': 1,
    'query': ''
}


def conf_read():
    config = configparser.ConfigParser()
    global verbosity_level

    def conf_init():
        print("> Initializing DEFAULT_CONFIG")
        config['STEAMGIFTS'] = CONFIG_DEFAULT
        with open('config.ini', 'w') as configfile: config.write(configfile)
        print("> Created file config.ini")

    if not len(config.read('config.ini')):
        conf_init()
        print("> Please paste the cookie \'PHPSESSID\' from steamgifts.com into the config.ini file!")
        input()
        sys.exit(0)
    elif not comp_lists(CONFIG_DEFAULT, config['STEAMGIFTS']):
        conf_init()
        print("> Error retrieving cookie PHPSESSID, please try pasting it again!")
        input()
        sys.exit(1)

    global min_points, kekse, min_points_on_page_refresh, refresh_sleep, pages, min_cost, queries
    try:
        min_points = config['STEAMGIFTS']['min_points']
        min_points_on_page_refresh = config['STEAMGIFTS']['min_points_on_page_refresh']
        refresh_sleep = config['STEAMGIFTS']['refresh_sleep']
        pages = config['STEAMGIFTS']['number_of_pages']
        min_cost = config['STEAMGIFTS']['min_giveaway_cost']
        verbosity_level = int(config['STEAMGIFTS']['verbosity_level'])
        kekse = {'PHPSESSID': config['STEAMGIFTS']['cookie']}
        queries = config['STEAMGIFTS']['query'].split(',')
    except:
        print("> Fatal error parsing config.ini, please check for formatting errors, or try generating a new one!")
        if verbosity_level > 2: print("> Awaiting user input to exit program")
        input()
        sys.exit(0)


def comp_lists(list1, list2):
    for x in list1.keys():
        if x not in list2.keys():
            return False
    return True


def get_soup_from_page(url):
    if verbosity_level > 1: print("> Loading request for " + str(url))
    r = requests.get(url, cookies=kekse)
    if verbosity_level > 2: print("> Trying to get html.parser soup for")
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup


def get_content():
    if verbosity_level > 1: print("> Getting steamgifts content")
    """
    Thanks to my great friend Stackoverflow
    """
    global xsrf_token, points

    try:
        if verbosity_level > 2: print("> Grabbing soup for steamgifts.com")
        soup = get_soup_from_page('https://www.steamgifts.com')
        if verbosity_level > 2: print("> Looking for xsrf token in soup content")
        xsrf_token = soup.find('input', {'name': 'xsrf_token'})['value']
        if verbosity_level > 2: print("> Filtering soup to get current points")
        points = soup.find('span', {'class': 'nav__points'}).text
    except RequestException:
        print("> Error connecting to steamgifts.com!")
        print("> Waiting 2 minutes and trying to reconnect...")
        sleep(120)
        get_content()
    except TypeError:
        print("> Invalid cookie! Aborting!")
        if verbosity_level > 2: print("> Awaiting user input to exit program")
        input()
        sys.exit(0)


def check(query, last=False):
    """ Loops through all the giveaways"""
    global title
    global entered

    print("> Current points: " + str(points))

    n = 1
    while n <= int(pages):
        print("> Loading giveaways page " + str(n) + "...")
        soup = get_soup_from_page('https://www.steamgifts.com/giveaways/search?page=' + str(n) + '&' + query)

        if soup.find_all('div', text='No results were found.'):
            break

        try:
            gifts_list = soup.find_all(
                lambda tag: tag.name == 'div' and tag.get('class') == ['giveaway__row-inner-wrap'])

            for item in gifts_list:
                if verbosity_level > 3: print(
                    "[DEBUG] Checking if points less than min_points {" + str(points) + " < " + str(min_points) + "}")
                if int(points) < int(min_points):
                    print("> Sleeping to get " + min_points + " points")
                    sleep((int(min_points) - int(points)) * 150)
                    check(query)
                    break

                if verbosity_level > 3: print(
                    "[DEBUG] Finding all 'span' elements with class 'giveaway__heading__thin'")

                giveaway_cost = item.find_all('span', {'class': 'giveaway__heading__thin'})

                last_div = None
                for last_div in giveaway_cost:
                    pass
                if last_div:
                    if verbosity_level > 3: print("[DEBUG] Getting giveaway cost from last_div")
                    giveaway_cost = last_div.getText().replace('(', '').replace(')', '').replace('P', '')
                    if verbosity_level > 3:
                        print("[DEBUG] Cost found: " + giveaway_cost)

                if verbosity_level > 3: print(
                    "[DEBUG] Getting name of the game from current giveaway, encoding in UTF-8")
                title = item.find('a', {'class': 'giveaway__heading__name'}).text.encode('utf-8')
                if verbosity_level > 3: print("[DEBUG] Getting ID from current giveaway")
                giveaway_id = item.find('a', {'class': 'giveaway__heading__name'})['href'].split('/')[2]
                if giveaway_id not in entered:
                    if verbosity_level > 3:
                        print(
                            "[DEBUG] Checks if giveaway__row-inner-wrap is-faded is not None -> giveaway already entered")
                    if item.find('div', {'class': 'giveaway__row-inner-wrap is-faded'}) is not None:
                        if verbosity_level > 3: print(
                            "[DEBUG] Giveaway already entered -> appending ID to entered list")
                        entered.append(giveaway_id)
                        continue
                    else:
                        if verbosity_level > 3: print("[DEBUG] Giveaway not entered, continuing")
                if int(giveaway_cost) < int(min_cost):
                    if verbosity_level > 3: print("[DEBUG] Giveaway ignored by config (min_points) ")
                    continue
                if (int(points) - int(giveaway_cost)) < 0 and (giveaway_id not in entered):
                    print(
                        "[-] Not enough points to enter: " + str(title, 'utf-8') + " (" + str(giveaway_cost) + ")")
                    sleep(1)
                    continue
                elif (int(points) - int(giveaway_cost)) > 0:
                    enter_giveaway(item, giveaway_cost)
            n += 1
        except AttributeError:
            print("> Error processing giveaways!")
            check(query)

    if int(points) < int(min_points_on_page_refresh):
        print("> Sleeping to get at least " + str(min_points_on_page_refresh) + " points")
        sleep((int(min_points_on_page_refresh) - int(points)) * 150)
    elif last:
        print("> No more giveaways. Sleeping for " + str(
            datetime.timedelta(seconds=int(refresh_sleep))) + "...")
        sleep(int(refresh_sleep))
    get_content()


def enter_giveaway(item, cost):
    giveaway_id = item.find('a', {'class': 'giveaway__heading__name'})['href'].split('/')[2]
    timestamps = item.find_all('span', {'data-timestamp': True})
    user = item.find('a', {'class': 'giveaway__username'})
    entries = (((item.find('div', {'class': 'giveaway__links'})).find_all('a')[0]).find('span'))

    entry = requests.post('https://www.steamgifts.com/ajax.php',
                          data={'xsrf_token': xsrf_token, 'do': 'entry_insert', 'code': giveaway_id}, cookies=kekse)
    json_data = json.loads(entry.text)

    get_content()

    if json_data['type'] == 'success':
        print("[+] Entered new giveaway [+]")
        print("Game: " + title.decode("utf-8"))
        print("Giveaway cost: " + str(cost))
        print("Points left: " + str(points))
        print("Created: " + str(timestamps[1].text) + " ago by user " + str(user.text))
        print("Time remaining: " + str(timestamps[0].text))
        print("Current entries: " + str(entries.text))
        print("[+] -------------------- [+]")
        entered.append(giveaway_id)
        sleep(randint(10, 30))


if __name__ == '__main__':
    entered = []
    print(" _           _ _______       _                      ")
    print("| |         | (_) ___ \     | |                     ")
    print("| |     ___ | |_| |_/ / ___ | |_ ______ _ __   __ _ ")
    print("| |    / _ \| | | ___ \/ _ \| __|______| '_ \ / _` |")
    print("| |___| (_) | | | |_/ / (_) | |_       | | | | (_| |")
    print("\_____/\___/|_|_\____/ \___/ \__|      |_| |_|\__, |")
    print("                                               __/ |")
    print("                                              |___/ ")
    print("> LoliBot-ng for SteamGifts v0.3 by hwky")
    print("> Not in any way affiliated with SteamGifts.com")
    print("> Use at your own risk!")
    sleep(5)
    os.system('cls')

    conf_read()
    get_content()
    if queries:
        while True:
            for q in queries:
                if q == queries[-1]:
                    check(q, True)
                else:
                    check(q)
    else:
        while True:
            check('', True)