'''Scrape info on series'''
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import requests
import pandas as pd
import time
import os
import json
from datetime import datetime
BASE_URL = "https://fmovies.to"
start = ""
retryCount = 0


def get_last_epi(series_name, season):

    query = '{0}+{1}'.format(
            '+'.join(series_name.split()), season)
    result = ""
    try:
        response = requests.get(
            '{0}/search?keyword={1}'.format(
                BASE_URL, query)
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        result = soup.find("a", class_="poster")
        result = result.get('href')

    except Exception as err:
        return "Connection error:{err}", 0
    except:
        return "Captcha content received", 0
    # delay before next request
    time.sleep(1)

    # Scrape last episode
    session = HTMLSession()
    try:
        req = session.get('{0}{1}'.format(BASE_URL, result))
    except:
        print("Couldn't connect to internet")
        raise SystemExit()

    req.html.render(timeout=5000)
    try:
        server = req.html.find('.episodes.range.active')[1]
        episodes = BeautifulSoup(server.html, 'html.parser')
        e = episodes.find_all("a")
        total_episodes = len(e)
        last_episode_link = e[-1].get('href')
        last_episode_num = int(e[-1].text)
    except:
        print(req.html)
        return None, 0
    req.close()
    session.close()
    return {
        "name": series_name, "latest_episode_num": last_episode_num,
        "latest_episode_link": '{0}{1}'.format(BASE_URL, last_episode_link),
        "season": season
    }, 1


def check_for_new_epi(series_name, season, watchedTill):
    global retryCount
    status = 0
    print("Looking up '{0} s{1}'...".format(series_name, season))
    retryCount = 0
    while not status:
        retryCount += 1
        info, status = get_last_epi(
            series_name.capitalize(), str(season)
        )
        if not status:
            print("Problem with connection. Retrying..")
            time.sleep(1)
        if retryCount >= 2:
            break
    try:
        diff = info['latest_episode_num'] - watchedTill
    except:
        print("Couldnt obtain data. Skipping...")
        return None
    print("DONE!")
    if(diff > 0):
        info["new_epi_count"] = diff
        return info
    return None


def seriesScraper():
    global start
    start = time.time()
    data = pd.read_csv('../data.csv', delimiter=',')
    series_name = data['series']
    season = data['season']
    watchedTill = data['epi']
    new_epi_of_series = []
    print('\nScraping metadata on the list of series ...\n')

    for i in range(len(series_name)):
        epi = check_for_new_epi(series_name[i], int(
            season[i]), int(watchedTill[i]))
        if epi:
            new_epi_of_series.append(epi)
        time.sleep(5)
        end = time.time()
        print("Time lapsed:{0}s".format(int(end-start)), end='\n')
    return new_epi_of_series


def main():
    new_epi_of_series = seriesScraper()
    pwd = os.getcwd()
    path_to_file = os.path.join(pwd, 'series.temp.json')

    if not os.path.exists(pwd) and not os.path.isfile(path_to_file):
        os.makedirs(path_to_file)
    try:
        with open(path_to_file, 'w') as f:
            data = {
                'data': new_epi_of_series,
                'date': datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            }
            f.write(json.dumps(data))
            f.close()
        if os.path.exists(os.path.join(pwd, 'series.json')):
            os.remove('series.json')
        os.rename('series.temp.json', 'series.json')
        print('Records updated.')
    except:
        print('Records were not updated.')


if __name__ == '__main__':
    main()
