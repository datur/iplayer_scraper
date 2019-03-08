import mechanicalsoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-setuid-sandbox")
        self.driver = webdriver.Chrome(options=options)

    def get_page(self, url):
        if validators.url(url):
            self.driver.get(url)
        html = self.driver.execute_script("return document.body.innerHTML")
        return html

    def get_curr_url(self):
        return self.driver.current_url
