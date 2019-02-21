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
            print(suffix)
            web_page = self.Browser.get_page(self._BASE_URL + suffix)

            program_selection = web_page.find_all(
                'li', attrs={"class": "grid__item"})

            # loop for each program on the current alphabet page
            for program_box in program_selection:

                latest_episode_url = self.iplayer_atoz_page_extractor(program_box)

                program_website_url = self.latest_episode_extractor(self._BASE_URL +
                                                                    latest_episode_url)

                # extract main information form the program website
                if program_website_url is not None:
                    self.program_microsite_extractor(program_website_url)

                self.dictionary.print()
                self.dictionary.clear()

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

        ''' TODO:
        - program medium synopsis
          this is held in: p-g-p no-margin-vertical ->
          first div tag with tag id grid__item map__item 1/2@gel3b
        - in the second div there are two sections containing now on
          ipayer and on tv which shows upcoming episodes
        - you may also like section would be nice to have to add
          to the recommendations
        '''
        try:
            self.program_synopsis(web_page)
        except Exception as e:
            print('Error ', e, ' at:', self._BASE_URL + program_website_url)

        self.supporting_content(web_page)

        self.full_recommend(self._BASE_URL + program_website_url + '/recommendations')

        self.episodes(web_page)

    def program_synopsis(self, web_page_element):
        '''will try to extract a longer program synopsis if available

        Arguments:
            web_page_element {beautiful soup element} -- html tag or element that can be searched
        '''

        long_synopsis = web_page_element.find(
            'div', attrs={'class': 'text--prose longest-synopsis'})

        if long_synopsis is None:
            long_synopsis = web_page_element.find(
                'div', attrs={'class': 'synopsis-toggle text--prose'})
            if long_synopsis is not None:
                long_synopsis = [x.get_text() for x in long_synopsis.find_all('p')]
                long_synopsis = ' '.join(long_synopsis) if long_synopsis is not None else None
                self.dictionary.add('long_synopsis', long_synopsis)

        if long_synopsis is None:
            long_synopsis = web_page_element.find(
                'div', attrs={'class': 'programme-info__text-container'})
            if long_synopsis is not None:
                long_synopsis = long_synopsis.find(
                    'p', attrs={'class': 'programme-info__description'})
                long_synopsis = long_synopsis.get_text() if long_synopsis is not None else None
                self.dictionary.add('long_synopsis', long_synopsis)

        if long_synopsis is None:
            long_synopsis = web_page_element.find(
                'p', attrs={'class': 'gel-brevier media__meta-row'})
            if long_synopsis is not None:
                long_synopsis = long_synopsis.get_text() if long_synopsis is not None else None
                self.dictionary.add('long_synopsis', long_synopsis)

    def supporting_content(self, web_page_element):
        '''will look for supporting content in the given webpage

        Arguments:
            web_page_element {beautifuloup element} -- should be related to a programme microsite
        '''

        supporting_content = web_page_element.find(
            'div', attrs={'class': 'grid__item mpu-grid__left'})
        if supporting_content is not None:
            supporting_content_list = supporting_content.find_all(
                'li', attrs={'class': 'grid__item tlec-page-card'})

            supporting_content_collection = []

            for content in supporting_content_list:
                content_details = content.find('div', attrs={'class': 'media__body'})
                link = content_details.find('a')
                content_link = link['href'] if link is not None else None
                content_datatype = content.div['data-object-type']
                content_name = link.get_text().strip()
                supporting_content_collection.append({'content_title': content_name,
                                                      'content_type': content_datatype,
                                                      'content_url': content_link})
            self.dictionary.add('supporting_content', supporting_content_collection)

    def full_recommend(self, url):
        '''if available the bbc iplayer recommendations for a program will be extracted

        Arguments:
            url {string of a url} -- this should be suffixed with '/recommendations'
        '''

        web_page = self.Browser.get_page(url)

        if web_page is not None:
            page_items = web_page.find(
                'ol', attrs={'class': 'highlight-box-wrapper'})

            if page_items is not None:
                recommendations = []
                list_items = page_items.find_all('li')

                for item in list_items:
                    item_info = item.find(
                        'div', attrs={'class': 'programme__body'})
                    link = item_info.h4.a['href']
                    _id = link.split('/')[-1]
                    # link_2 = item_info.h4.a['resource']
                    title = item_info.h4.a.get_text()
                    synop = item_info.p.get_text()

                    recommendations.append({
                        'id': _id,
                        'title': title,
                        'synopsis': synop,
                        'link': link
                    })
                self.dictionary.add('recommendations', recommendations)

    def episodes(self, web_page):

        episodes_link = web_page.find(
            'a',
            attrs={
                'class': 'br-nav__link',
                'data-linktrack': 'nav_episodes'
            })

        if episodes_link is not None:

            episodes_link = episodes_link['href']

            episodes_page = self.Browser.get_page(self._BASE_URL +
                                                  episodes_link)

            episodes_available = []
            episodes_available.append(self.episode_list_extractor(episodes_page))

            episode_pagination = episodes_page.find(
                'ol', attrs={'class': 'nav nav--banner pagination delta'})

            if episode_pagination:
                page_list = episode_pagination.find_all(
                    'li', attrs={'class': 'pagination__page'})
                page_links = [
                    x.a['href'] for x in page_list if x.a is not None
                ]

                for endpoint in page_links:
                    url = self._BASE_URL + episodes_link + endpoint

                    episodes_page = self.Browser.get_page(url)
                    episodes_available.append(self.episode_list_extractor(episodes_page))

            # next_on = episodes_page.find(
            #     'ul', attrs={
            #         'class': 'list-unstyled cf delta'
            #     }).find_all('li')

            # if next_on[-1].a:
            #     episodes_upcoming = self.upcoming_episodes(next_on[-1].a)

    def episode_list_extractor(self, web_page):

        episodes_available_list = web_page.find(
            'ol', attrs={'class': 'highlight-box-wrapper'})
        episodes_container_list = episodes_available_list.find_all('div', recursive=False)

        episodes_list = []

        # TODO: fix this
        # TODO need to go through each episode and extract credits

        for item in episodes_container_list:
            # link

            _id = item['data-pid']

            episode_dict = {_id: {}}

            episode_link = item.find('a', attrs={'class': 'br-blocklink__link block-link__target'})
            episode_link = episode_link['href']
            episode_dict[_id].update({'episode_link': episode_link})

            episode_title = item.find('span', attrs={'class': 'programme__title gamma'})
            episode_title = episode_title.get_text()
            episode_dict[_id].update({'episode_title': episode_title})

            episode_synopsis = item.find(
                'p', attrs={'class': 'programme__synopsis text--subtle centi'})

            if episode_synopsis.find('abbr'):
                series_position = episode_synopsis.find(
                    'abbr').find('span', datatype=True).get_text()
                series_num_episodes = episode_synopsis.find('abbr').find(
                    'span', attrs={'class': 'programme__groupsize'}).get_text()

                episode_dict[_id].update({'series_position': series_position})
                episode_dict[_id].update({'series_num_episodes': series_num_episodes})

            episode_synopsis = episode_synopsis.find('span', recursive=False).get_text()
            episode_dict[_id].update({'episode_synopsis': episode_synopsis})

            episode_time_left = item.find('div', attrs={'class': 'cta cta__overlay'})
            episode_time_left = episode_time_left.a['title']
            episode_dict[_id].update({'episode_time_left': episode_time_left})

            episode_web_page = self.Browser.get_page(episode_link)

            main_episode_info = episode_web_page.find(
                'div', attrs={'class': 'grid-wrapper grid-wrapper--flush map map--episode map--count-2'})

            episode_longest_synopsis = main_episode_info.find(
                'div', attrs={'class': 'text--prose longest-synopsis'})

            series_id = main_episode_info.find('div', attrs={'class': 'offset'}).find_all('a')
            series_id = series_id[-1]['href']
            series_name = series_id[-1].get_text()

            left_to_watch = web_page.find(
                'div', attrs={'class': 'grid 1/3@bpw 1/4@bpe'})

            if left_to_watch is not None:
                left_to_watch_items = left_to_watch.find_all(
                    'p', attrs={'class': 'episode-panel__meta'})

                if left_to_watch.find(
                        'div', attrs={'class': "episode-panel__meta"}) is None:
                    if left_to_watch_items[0].span is None:
                        days_left = left_to_watch_items[0].get_text()
                    else:
                        days_left = left_to_watch_items[0].span.get_text()
                    duration = left_to_watch_items[1].get_text()

            # grid 1/3@bpw 1/4@bpe - broadcast information

            # find grid-wrapper grid-wrapper--flush map map--episode map--count-2 (main episode info)
            # find island where synopsis is kept

            # find grid 1/3@bpw2 1/3@bpe map__column map__column--2 map__column--last
            # find br-box-secondary containing the last broadcast infomration
            # find broadcast information component component--box component--box--primary
            # get genre
            # get credits

            # list of mucic played list-unstyled segments-list__items
            # get time left to watch and duration

            episodes_list.append(episode_dict)

        self.dictionary.add('episodes', episodes_list)

        return episodes_list

    def upcoming_episodes(self, url):
        '''next_on_suffix = 'broadcasts/upcoming/'''
        web_page = self.Browser.get_page(self._BASE_URL + url +
                                         '/broadcasts/upcoming')

        next_on_section = web_page.find(
            'ol', attrs={'class': 'highlight-box-wrapper'})

        next_up = []
        if next_on_section:

            for item in next_on_section.find_all('li'):
                broadcast_info = item.find(
                    'div',
                    attrs={'class': 'programme__body programme__body--flush'})
                broadcast_info_tag = broadcast_info.find(
                    'div', attrs={'class': 'broadcast-event__time beta'})

                broadcast_date = broadcast_info_tag['title']
                broadcast_day = broadcast_info_tag.find(
                    'span',
                    attrs={
                        'class':
                        'broadcast-event__date text-base timezone--date'
                    }).get_text()
                broadcast_time = broadcast_info_tag.find(
                    'span', attrs={
                        'class': 'timezone--time'
                    }).get_text()

                broadcast_channel = broadcast_info.find(
                    'div',
                    attrs={
                        'class':
                        'programme__service box-link__elevated micro text--subtle'
                    })

                channel = broadcast_channel.a.get_text()
                channel_url = broadcast_channel.a['href']

                program_info = item.find(
                    'div',
                    attrs={
                        'class': 'grid 7/12 2/3@bpb2 3/4@bpw 5/6@bpw2 5/6@bpe'
                    })
                program_title_info = program_info.find(
                    'a',
                    attrs={'class': 'br-blocklink__link block-link__target'})

                program_id = program_info.find(
                    'div',
                    attrs={
                        'class':
                        'programme programme--tv programme--episode block-link'
                    })
                if program_id is not None:
                    program_id = program_id['data-pid']
                else:
                    program_id = program_info.find(
                        'div',
                        attrs={
                            'class':
                            'programme programme--radio programme--episode block-link'
                        })
                    if program_id is not None:
                        program_id = program_id['data-pid']
                    else:
                        program_id = program_info.find(
                            'div',
                            attrs={
                                'class':
                                'programme programme--episode block-link'
                            })['data-pid']

                program_link = program_title_info['href']
                program_title = program_title_info.find(
                    'span', attrs={'class': 'programme__title gamma'})

                if program_title is not None:
                    program_title = program_title.get_text()
                else:
                    print(program_title_info)
                series = program_title_info.find(
                    'span', attrs={'class': 'programme__subtitle centi'})
                if series:
                    series = series.get_text()
                else:
                    series = None
                program_synopsis = program_info.p.get_text()

                temp_dict = {
                    program_id.strip(): {
                        'program_title': program_title.strip(),
                        'series': series,
                        'program_synopsis': program_synopsis.strip(),
                        'program_link': program_link,
                        'channel': {
                            'name': channel,
                            'link': channel_url
                        },
                        'broadcast': {
                            'date': broadcast_date,
                            'day': broadcast_day,
                            'time': broadcast_time
                        }
                    }
                }

                next_up.append(temp_dict)
            return next_up

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


# testing

X = Extractor()

X.extract()
