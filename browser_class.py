# browser class for iplayer scraper v0.1
import mechanicalsoup
from selenium import webdriver
import validators


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


class JSBrowser(object):

    def __init__(self):
        web_driver_options = webdriver.ChromeOptions()
        web_driver_options.add_argument('headless')
        self.driver = webdriver.Chrome(options=web_driver_options)

    def get_page(self, url):
        if validators.url(url):
            self.driver.get(url)
        html = self.driver.execute_script("return document.body.innerHTML")
        return html

    def get_curr_url(self):
        return self.driver.current_url
