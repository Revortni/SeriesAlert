'''Scrape info on series'''
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from pprint import pprint
import requests
import pandas as pd
import time

BASE_URL = "https://fmovies.to"
start = ""


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
    req = session.get('{0}{1}'.format(BASE_URL, result))
    req.html.render(timeout=20000)
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
    status = 0
    print("Looking up '{0} s{1}'...".format(series_name, season), end="")
    while not status:
        info, status = get_last_epi(
            series_name.capitalize(), str(season)
        )

        if not status:
            print("Problem with connection. Retrying..")
    print("DONE!")
    diff = info['latest_episode_num'] - watchedTill
    if(diff > 0):
        info["new_epi_count"] = diff
        return info
    return None


def seriesScraper():
    data = pd.read_csv('./data.csv', delimiter=',')
    series_name = data['series']
    season = data['season']
    watchedTill = data['epi']
    new_epi_of_series = []
    print('\nScraping metadata on the list of series ...\n')

    for i in range(len(series_name)):
        epi = check_for_new_epi(series_name[i], season[i], watchedTill[i])
        if epi:
            new_epi_of_series.append(epi)
        time.sleep(5)
        end = time.time()
        print("Time lapsed:{0}s".format(int(end-start)), end='\n')
    return new_epi_of_series


def main():
    global start
    start = time.time()
    new_epi_of_series = seriesScraper()
    if new_epi_of_series:
        print("\nCongratz! Looks like you've got some new episodes for the following:")
        for i in new_epi_of_series:
            print(i, end='\n\n')
        print("Update your episode number when you watch the episode.")
    else:
        print("Oops. Guess no new episodes for any of your series are available .")


if __name__ == '__main__':
    main()
