'''Scrape info on series'''

from PyQt4.QtWebKit import QWebPage
from PyQt4.QtCore import QUrl
from PyQt4.QtGui import QApplication
import sys
from bs4 import BeautifulSoup
from pprint import pprint
import requests
import pandas as pd

BASE_URL = "https://fmovies.to"


class Client(QWebPage):

    def __init__(self, url):
        self.app = QApplication(sys.argv)
        QWebPage.__init__(self)
        self.loadFinished.connect(self.on_page_load)
        self.mainFrame().load(QUrl(url))
        self.app.exec_()

    def on_page_load(self):
        self.app.quit()


def get_last_epi(series_name, season):

    query = '{0}+{1}'.format('+'.join(series_name.split()
                                      ), season)
    req = requests.get('{0}/search?keyword={1}'.format(BASE_URL, str(query)))
    soup = BeautifulSoup(req.text, 'html.parser')
    result = soup.find("a", class_="poster")
    result = result.get('href')

    # Scrape last episode
    url = '{0}{1}'.format(BASE_URL, result)
    client_response = Client(url)
    source = client_response.mainFrame().toHtml()
    client_response.on_page_load()
    soup = BeautifulSoup(source, 'html.parser')
    episodes = soup.select('ul.episodes.range.active')[0]
    e = episodes.find_all("a")
    total_episodes = len(e)
    last_episode_link = e[-1].get('href')
    last_episode_num = e[-1].text
    return {
        "name": series_name, "latest_episode_num": last_episode_num,
        "latest_episode_link": '{0}{1}'.format(BASE_URL, last_episode_link),
        "season": season
    }


def main():
    data = pd.read_csv('./data.csv', delimiter=',')
    series_name = data['series']
    season = data['season']
    info = []
    print('\nScraping metadata on the list of series ...\n\n')
    for i in range((len(series_name))):
        print("Looking up '{0} s{1}'...".format(series_name[i], season[i]))
        print(get_last_epi(series_name[i].capitalize(), str(
            season[i])), end='\n\n\n')


if __name__ == '__main__':
    main()
