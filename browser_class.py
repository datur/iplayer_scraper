import mechanicalsoup


class Browser(object):
    """docstring for Browser"""

    def __init__(self):
        self.browser = mechanicalsoup.StatefulBrowser()
        self.current_url = None
        self._BASE_URL = 'https://bbc.co.uk'

    def get_page(self, url):
        self.browser.open(url)
        self.current_url = url
        return self.browser.get_current_page()

    def get_url(self):
        return self.current_url

