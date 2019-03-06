from Extractor import Extractor
from browser_class import Browser, JSBrowser
from bs4 import BeautifulSoup
import time


def test(url):
    '''method for testing the extractor for the iplayer scraper

    Arguments:
        url {the url of a desired episode programme page}
    '''
    J = JSBrowser()

    for u in url:
        print('starting browser navigation')
        print(B._BASE_URL + u)

        resp = J.navigate(B._BASE_URL + u)

        web_page = BeautifulSoup(resp, 'lxml')

        programme_dict = X.extract_childrens(web_page)

        print(programme_dict)


X = Extractor()
B = Browser()


cbbc_url = '/cbbc/shows/all-over-the-workplace'
cbeebies_url = '/cbeebies/shows/molly-and-mack'

print('cbeebies test:')
test([cbeebies_url, cbbc_url])
