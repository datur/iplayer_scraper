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
url2 = '/programmes/p02b4jth'
eastenders = '/programmes/b006m86d'


# test(url=url1)
# test(url=url2)
test(eastenders)
