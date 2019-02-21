from bs4 import BeautifulSoup
from browser_class import Browser
from dictionary_builder import DictionaryBuilder
from datetime import datetime


class Extractor(object):
    """docstring for Extractor"""

    def __init__(self):
        super(Extractor, self).__init__()
        self.Browser = Browser()
        self.dictionary = DictionaryBuilder()
        self._BASE_URL = 'https://www.bbc.co.uk'
        self._SCRAPING_SUFFIX = '/iplayer/a-z/'

    def extract(self):
        '''main extractor method. This will return a dictionary'''

        filename = str('bbc_iplayer_scraped_' +
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '.json')

        initial_page = self.Browser.get_page(self._BASE_URL +
                                             self._SCRAPING_SUFFIX)

        atoz = initial_page.find('div', attrs={'class': "atoz-nav__inner"})

        navigation = atoz.find('ul', attrs={'class': 'scrollable-nav__track'})

        navigation_list = navigation.find_all('li')

        navigation_list = [
            x.a['href'] for x in navigation_list if x.a is not None
        ]

        # for loop for each page in a-z
        for suffix in navigation_list:

            web_page = self.Browser.get_page(self._BASE_URL + suffix)

            program_selection = web_page.find_all(
                'li', attrs={"class": "grid__item"})

            # loop for each program on the current alphabet page
            for program_box in program_selection:

                latest_episode_url = self.iplayer_atoz_page_extractor(program_box)

                program_website_url = self.latest_episode_extractor(self._BASE_URL +
                                                            latest_episode_url)

                # extract main information form the program website
                self.program_microsite_extractor(program_website_url)

                print(self.dictionary.print())

    def iplayer_atoz_page_extractor(self, program_selection):
        '''arguement is soup div tag for a program.
        Returns a dictionary containingprogram title,
        program synopsis, no of episodes available, and
        the link to the latest episode
       '''

        # Program Title
        title = program_selection.find(
            'p', attrs={'class': 'list-content-item__title'})

        if title is not None:
            title = title.get_text()
        else:
            title = program_selection.find(
                'div', attrs={'class': 'content-item__title'})
            if title is not None:
                title = title.get_text()

        # Program Synopsis
        synopsis = program_selection.find(
            'p', attrs={'class': 'list-content-item__synopsis'})

        if synopsis is not None:
            synopsis = synopsis.get_text()
        else:
            synopsis = program_selection.find(
                'div', attrs={'class': 'content-item__description'})
            if synopsis is not None:
                synopsis = synopsis.get_text()

        # Link to latest episode
        latest_episode_url = program_selection.find('a', href=True)['href']

        # Number of episodes available
        episodes_available = program_selection.find(
            'div', attrs={'class': 'list-content-item__sublabels'})

        if episodes_available is not None:
            episodes_available = episodes_available.get_text()

        self.dictionary.add('title', title)
        self.dictionary.add('short_synopsis', synopsis)
        self.dictionary.add(
            'episodes_available',
            episodes_available.split(' ')[0]
            if episodes_available is not None else None)

        return latest_episode_url

    def latest_episode_extractor(self, latest_episode_url):
        ''' input latest_episode_url '''

        web_page = self.Browser.get_page(latest_episode_url)

        if web_page is not None:
            program_website_url = web_page.find(
                'a', attrs={'class': 'lnk'}, text='Programme website')
        else:
            print('\n\n\n', latest_episode_url, '\n\n\n')

        if program_website_url:
            program_website_url = program_website_url['href']

        return program_website_url

    def program_microsite_extractor(self, program_website_url):
        ''' gets information from the programmes microsite '''
        web_page = self.Browser.get_page(self._BASE_URL + program_website_url)

        genre_format = self.get_genre_format(web_page)

        print(genre_format)

    # TODO this needs rewriting asap
    def get_genre_format(self, web_page):
        genre_format = web_page.find(
            'div', attrs={'class': 'footer__similar b-g-p component'})

        if genre_format is None:
            genre_format = web_page.find(
                'div',
                attrs={
                    'class':
                    'islet--horizontal footer__programmes footer__service-island'
                })

        if genre_format is not None:
            sim = genre_format.find_all('div')
            genre_format_list = []

            for i in sim:
                genre_format_list.append([[x.get_text(), x['href']]
                                          for x in i.find_all('a', href=True)])

            genre_format_dict = {'genre': {}}

            # TODO this should be re-written into lists of dictionaries also handle multiple sub genres better 

            for i in range(len(genre_format_list)):
                for j in range(len(genre_format_list[i])):
                    if i == 0:
                        if j < 1:
                            genre_format_dict['genre'].update({
                                'main': {
                                    str(j): genre_format_list[i][j][0],
                                    'link': genre_format_list[i][j][1]
                                }
                            })
                        elif j == 1:
                            genre_format_dict['genre'].update({
                                'sub_genre': {
                                    str(j): genre_format_list[i][j][0],
                                    'link': genre_format_list[i][j][1]
                                }
                            })
                        else:
                            genre_format_dict['genre']['sub_genre'].update({
                                str(j):
                                genre_format_list[i][j][0],
                                'link':
                                genre_format_list[i][j][1]
                            })
                    else:
                        if j < 1:
                            genre_format_dict.update({
                                'format': {
                                    str(j): genre_format_list[i][j][0],
                                    'link': genre_format_list[i][j][1]
                                }
                            })
                        else:
                            genre_format_dict['format'].update({
                                'sub_format': {
                                    str(j): genre_format_list[i][j][0],
                                    'link': genre_format_list[i][j][1]
                                }
                            })
            return genre_format_dict

#testing

X = Extractor()

X.extract()
