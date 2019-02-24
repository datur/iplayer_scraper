from Extractor import Extractor
from browser_class import Browser


def test(url):
    '''method for testing the extractor for the iplayer scraper

    Arguments:
        url {the url of a desired episode programme page}
    '''

    X.program_microsite_extractor(url)
    X.dictionary.print()


X = Extractor()
B = Browser()

url1 = '/programmes/b0bxbvtl'
url2 = 'https://www.bbc.co.uk/programmes/p02b4jth'


test(url=url1)
