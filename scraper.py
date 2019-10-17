'''Scrape info on series'''
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from pprint import pprint
import requests
import pandas as pd
import time

BASE_URL = "https://fmovies.to"


def get_last_epi(series_name, season):

    query = '{0}+{1}'.format(
            '+'.join(series_name.split()), season)
    try:
        res = requests.get(
            '{0}/search?keyword={1}'.format(BASE_URL, str(query))
        )
        if res.status_code != 200:
            return ConnectionRefusedError
        soup = BeautifulSoup(res.text, 'html.parser')
        print(soup)
        result = soup.find("a", class_="poster")
        result = result.get('href')
    except ConnectionRefusedError:
        return "Fmovies refused to connect"
    except:
        return "Connection error"

    # Scrape last episode
    session = HTMLSession()
    req = session.get('{0}{1}'.format(BASE_URL, result))
    req.html.render(timeout=40000)

    server = req.html.find('.episodes.range.active')[0]
    episodes = BeautifulSoup(server.html, 'html.parser')
    e = episodes.find_all("a")
    total_episodes = len(e)
    last_episode_link = e[-1].get('href')
    last_episode_num = e[-1].text
    req.close()
    session.close()
    return {
        "name": series_name, "latest_episode_num": last_episode_num,
        "latest_episode_link": '{0}{1}'.format(BASE_URL, last_episode_link),
        "season": season
    }


def main():
    data = pd.read_csv('./data.csv', delimiter=',')
    series_name = data['series']
    season = data['season']

    print('\nScraping metadata on the list of series ...\n\n')
    for i in range(len(series_name)):
        print("Looking up '{0} s{1}'...".format(series_name[i], season[i]))
        info = get_last_epi(series_name[i].capitalize(), str(season[i]))
        print(info, end="\n\n\n")


if __name__ == '__main__':
    main()
