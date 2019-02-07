# extractor class
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

        initial_page = self.Browser.get_page(self._BASE_URL +
                                             self._SCRAPING_SUFFIX)

        navigation = initial_page.find(
            'ul', attrs={'class': 'scrollable-nav__track'})
        navigation_list = navigation.find_all('li')
        navigation_list = [
            x.a['href'] for x in navigation_list if x.a is not None
        ]

        # Main loop for the [a-z] apges of iplayer
        for suffix in navigation_list:
            web_page = self.Browser.get_page(self._BASE_URL + suffix)
            program_selection = web_page.find_all(
                'li', attrs={"class": "grid__item"})

            # loop for each program on the current alphabet page
            for program_box in program_selection:
                program_info = self.iplayer_atoz_page_extractor(program_box)

                program_website_info = self.programme_website_extractor(
                    self._BASE_URL + program_info['latest_episode_url'])

                if program_website_info['program_website_url'] is None:
                    print(program_website_info, program_info)

                if program_website_info['program_website_url'] is not None:
                    _id = self.get_program_id(
                        program_website_info['program_website_url'])
                else:
                    _id = self.get_program_id(
                        program_info['latest_episode_url'], flag=False)

                self.dictionary.add({_id: program_info})
                self.dictionary.update(_id, program_website_info)

                if program_website_info[
                        'program_website_url'] and program_website_info[
                            'program_credits_url']:
                    latest_episode_info = self.latest_episode_page(
                        program_website_info['program_credits_url']
                        if program_website_info['credits_available'] else
                        program_website_info['program_website_url'],
                        program_website_info['credits_available'],
                        program_website_info['program_website_url'])
                    self.dictionary.update(_id, latest_episode_info)

        self.dictionary.to_file('bbc_iplayer_scraped_' +
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                                '.json')

    def get_program_id(self, url, flag=True):
        '''takes the program bebsite url and trturns the
        unique program id
        '''
        if flag:
            return url.split('/')[-1]
        else:
            return url.split('/')[2]

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
            print(program_selection)
        # Program Synopsis
        synopsis = program_selection.find(
            'p', attrs={
                'class': 'list-content-item__synopsis'
            }).get_text()
        # Link to latest episode
        latest_episode_url = program_selection.find('a', href=True)['href']
        # Number of episodes available
        episodes_available = program_selection.find(
            'div', attrs={
                'class': 'list-content-item__sublabels'
            }).get_text()

        return {
            'title': title,
            'synopsis': synopsis,
            'latest_episode_url': latest_episode_url,
            'episodes_available': episodes_available
        }

    def programme_website_extractor(self, latest_episode_url):
        ''' input latest_episode_url '''
        web_page = self.Browser.get_page(latest_episode_url)

        program_website_url = web_page.find(
            'a', attrs={'class': 'lnk'}, text='Programme website')

        program_credits_url = web_page.find(
            'a', attrs={'class': 'lnk'}, text='Credits')

        credits_available = bool(program_credits_url)

        if credits_available:
            program_credits_url = program_credits_url['href']
        if program_website_url:
            program_website_url = program_website_url['href']

        return {
            'program_website_url': program_website_url,
            'program_credits_url': program_credits_url,
            'credits_available': credits_available
        }

    def latest_episode_page(self, url, credits_available, prog_base_url):
        '''args: either program_website_url or credits_url if avaiable '''

        web_page = self.Browser.get_page(self._BASE_URL + url)

        if credits_available:
            credits = self.get_credits(web_page)
        else:
            credits = None

        genre_format = self.get_genre_format(web_page)

        left_to_watch_and_duration = self.get_left_to_watch(web_page)

        long_synopsis = self.get_long_synopsis(web_page)

        broadcast_info = self.get_broadcast_info(web_page)

        recommendations = self.iplayer_recmmendations(web_page)

        available_episodes = self.episode_available_extraction(
            web_page, prog_base_url)

        return {
            'credits': credits,
            'genre_format': genre_format,
            'left_to_watch': left_to_watch_and_duration['left_to_watch'],
            'duration': left_to_watch_and_duration['duration'],
            'long_synopsis': long_synopsis,
            'broadcast_info': broadcast_info,
            'recommendations': recommendations,
            'available_episodes': available_episodes
        }

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

    def get_credits(self, web_page):
        '''extracts credits from iplayer webpage if available '''
        credits = web_page.find('table', attrs={'class': 'table'})
        if credits:
            credits_dict = {}
            for row in credits.find_all('tr'):
                person = row.find_all('span')
                if len(person) > 1:
                    json_credits = [x.get_text() for x in person]
                    credits_dict[json_credits[0]] = json_credits[1]
            return credits_dict
        else:
            return None

    def get_left_to_watch(self, web_page):
        '''gets the days left to watch the current program '''

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

                return {
                    'left_to_watch': days_left.strip(),
                    'duration': duration.strip()
                }
        return {'left_to_watch': None, 'duration': None}

    def get_long_synopsis(self, web_page):
        long_synopsis = web_page.find(
            'div', attrs={'class': 'synopsis-toggle__long'})

        if long_synopsis is not None:
            long_synopsis_paragraphs = [
                x.get_text() for x in long_synopsis.find_all('p')
            ]
        else:
            long_synopsis_paragraphs = None
        return {'long_synopsis': long_synopsis_paragraphs}

    def get_broadcast_info(self, web_page):
        main_broadcast = web_page.find(
            'div',
            attrs={
                'class':
                'grid 1/3@bpw2 1/3@bpe map__column map__column--2 map__column--last'
            })

        if main_broadcast is not None:
            date_last_aired = main_broadcast.find(
                'span',
                attrs={
                    'class': 'broadcast-event__date text-base timezone--date'
                })
            time_last_aired = main_broadcast.find(
                'span', attrs={'class': 'timezone--time'})
            channel = main_broadcast.find(
                'div',
                attrs={
                    'class':
                    'programme__service box-link__elevated micro text--subtle'
                })

            if channel is not None:
                if channel.find('a'):
                    channel_text = channel.find('a').get_text()
                else:
                    channel_text = None
            else:
                channel_text = None

            if channel is not None:
                if channel.find('a'):
                    channel_link = channel.find('a')['href']
                else:
                    channel_link = None
            else:
                channel_link = None

            if date_last_aired is not None:
                date_last_aired = date_last_aired.get_text()
            else:
                date_last_aired = None

            if time_last_aired is not None:
                time_last_aired = time_last_aired.get_text()
            else:
                time_last_aired = None

            return {
                'channel_text': channel_text,
                'channel_link': channel_link,
                'date_last_aired': date_last_aired,
                'time_last_aired': time_last_aired
            }

        else:
            return None, None, None, None

    def iplayer_recmmendations(self, web_page):
        '''docstring '''
        if web_page is not None:
            page_items = web_page.find(
                'ol', attrs={'class': 'highlight-box-wrapper'})

        if page_items is not None:
            list_items = page_items.find_all('li')
            recommendations = {'recommendations': {}}
            for item in list_items:
                item_info = item.find(
                    'div', attrs={'class': 'programme__body'})
                link = item_info.h4.a['href']
                _id = link.split('/')[-1]
                # link_2 = item_info.h4.a['resource']
                title = item_info.h4.a.get_text()
                synop = item_info.p.get_text()
                recommendations['recommendations'].update({
                    _id: {
                        'title': title,
                        'synopsis': synop,
                        'link': link
                    }
                })
            return recommendations
        else:
            return None

    # Testing purposes
    def episode_single_program(self, url):
        out = self.episode_available_extraction(
            self.Browser.get_page(url), url)
        return out

    def episode_available_extraction(self, web_page, episode_base_url):
        ''' args soup webpage '''

        episodes_link = web_page.find(
            'a',
            attrs={
                'class': 'br-nav__link',
                'data-linktrack': 'nav_episodes'
            })

        if episodes_link is not None:
            episodes_link = episodes_link['href']

            episodes_available_dict = {
                'episodes': {
                    'available_episodes': {},
                    'upcoming_episodes': {}
                }
            }

            episodes_page = self.Browser.get_page(self._BASE_URL +
                                                  episodes_link)

            episodes_available_dict['episodes']['available_episodes'].update(
                self.episode_list_extractor(episodes_page))

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
                    episodes_available_dict['episodes'][
                        'available_episodes'].update(
                            self.episode_list_extractor(episodes_page))

            next_on = episodes_page.find(
                'ul', attrs={
                    'class': 'list-unstyled cf delta'
                }).find_all('li')

            if next_on[-1].a:
                episodes_available_dict['episodes'][
                    'upcoming_episodes'].update(
                        self.upcoming_episodes(episode_base_url))

            return episodes_available_dict
        else:
            return None

    def episode_list_extractor(self, web_page):
        episodes_available_list = web_page.find(
            'div', attrs={'class': 'br-box-page programmes-page'})
        episodes_container_list = episodes_available_list.find_all(
            'div',
            attrs={
                'class':
                'programme programme--tv programme--episode block-link highlight-box--list br-keyline br-blocklink-page br-page-linkhover-onbg015--hover'
            })

        available_episodes = web_page.find(
            'span',
            attrs={'class': 'hidden grid-visible@bpb2 grid-visible@bpw'})

        episodes_available_dict = {}

        #TODO: fix this implimentation
        for item in episodes_container_list:
            # link

            item_headder = item.find(
                'div', attrs={'class': 'cta cta__overlay'})
            item_link = item_headder.a['href']
            # time left
            item_time_left = item_headder.a['title']
            # title
            item_body = item.find('div', attrs={'class': 'programme__body'})

            if item_body is not None:
                # num of episodes
                try:
                    episode_oneline_synopsis = item_body.p.get_text()
                except:
                    pass
                try:
                    episode_no = item_body.p.abbr['title']
                except:
                    episode_no = None
                    pass
                try:
                    episode_title = item_body.find(
                        'span', attrs={
                            'class': 'programme__title gamma'
                        }).get_text()
                except:
                    pass
                item_id = item_link.split('/')[-1]
                episodes_available_dict.update({
                    item_id: {
                        'title': episode_title,
                        'episode_no': episode_no,
                        'synopsis': episode_oneline_synopsis,
                        'link': item_link,
                        'time_left': item_time_left
                    }
                })

            else:
                episodes_available_dict = None

        return episodes_available_dict

    def upcoming_episodes(self, url):
        '''next_on_suffix = 'broadcasts/upcoming/'''
        web_page = self.Browser.get_page(self._BASE_URL + url +
                                         '/broadcasts/upcoming')

        next_on_section = web_page.find(
            'ol', attrs={'class': 'highlight-box-wrapper'})

        next_up_dict = {}
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

                next_up_dict.update(temp_dict)

        return next_up_dict
