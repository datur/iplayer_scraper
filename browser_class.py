# browser class for iplayer scraper v0.1
import mechanicalsoup
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEnginePage


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


class JSBrowser(QWebEnginePage):
    ''' usage: jsbrowser_resp = JSBrowser(url)
        html_content = jsbrowser_resp.html

    Arguments:
        QWebEnginePage {url} -- url string

    '''

    def __init__(self):
        self.app = QApplication(sys.argv)
        QWebEnginePage.__init__(self)
        self.loadFinished.connect(self.on_page_load)
        self.html = ''

    def navigate(self, url):
        print('load startedfor: ', url)
        self.html = ''
        self.load(QUrl(url))
        self.app.exec_()
        return self.html

    def on_page_load(self):
        self.html = self.toHtml(self.Callable)
        print('Load finished')

    def Callable(self, html_str):
        self.html = html_str
        self.app.quit()
