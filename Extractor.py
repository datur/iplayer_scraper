from bs4 import BeautifulSoup
from browser_class import Browser
from dictionary_builder import DictionaryBuilder
from datetime import datetime


class Extractor(object):
    ''' main extractor class for the bbc iplayer scraper
    '''

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

        # todo: check for channel then execute kids show extractor

        genres, formats = self.get_genre(web_page)
        self.dictionary.add('genre', genres)
        self.dictionary.add('format', formats)

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
                    tmp_dict = {}
                    item_info = item.find(
                        'div', attrs={'class': 'programme__body'})
                    link = item_info.h4.a['href']
                    _id = link.split('/')[-1]
                    # link_2 = item_info.h4.a['resource']
                    title = item_info.h4.a.get_text()
                    synop = item_info.p.get_text()
                    episode_microsite = self.episode_microsite_extractor(self._BASE_URL + link)

                    tmp_dict.update({
                        'id': _id,
                        'title': title,
                        'synopsis': synop,
                        'link': link
                    })
                    tmp_dict.update(episode_microsite)
                    recommendations.append(tmp_dict)
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

            # debug
            # print(episodes_link)

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

            next_on = episodes_page.find(
                'ul', attrs={
                    'class': 'list-unstyled cf delta'
                }).find_all('li')

            if next_on[-1].a:
                episodes_upcoming = self.upcoming_episodes(next_on[-1].a['href'])
                episodes_available.append(episodes_upcoming)

    def episode_list_extractor(self, web_page):

        episodes_available_list = web_page.find(
            'ol', attrs={'class': 'highlight-box-wrapper'})
        episodes_container_list = episodes_available_list.find_all('div', recursive=False)

        episodes_list = []

        for item in episodes_container_list:
            # link

            _id = item['data-pid']

            episode_dict = {'episode': {}}

            episode_dict['episode'].update({'id': _id})

            episode_link = item.find('a', attrs={'class': 'br-blocklink__link block-link__target'})
            episode_link = episode_link['href']
            episode_dict['episode'].update({'episode_link': episode_link})

            episode_title = item.find('span', attrs={'class': 'programme__title gamma'})

            episode_title = episode_title.get_text()
            episode_dict['episode'].update({'episode_title': episode_title})

            episode_synopsis = item.find(
                'p', attrs={'class': 'programme__synopsis text--subtle centi'})

            if episode_synopsis.find('abbr'):
                series_position = episode_synopsis.find(
                    'abbr').find('span', datatype=True).get_text()
                series_num_episodes = episode_synopsis.find('abbr').find(
                    'span', attrs={'class': 'programme__groupsize'}).get_text()

                episode_dict['episode'].update({'series_position': series_position})
                episode_dict['episode'].update({'series_num_episodes': series_num_episodes})

            episode_synopsis = episode_synopsis.find('span', recursive=False).get_text()
            episode_dict['episode'].update({'episode_synopsis': episode_synopsis})

            episode_time_left = item.find('div', attrs={'class': 'cta cta__overlay'})
            episode_time_left = episode_time_left.a['title']
            episode_dict['episode'].update({'episode_time_left': episode_time_left})

            # TODO this should be refactored
            episode_web_page = self.Browser.get_page(episode_link)

            main_episode_info = episode_web_page.find(
                'div', attrs={'class': 'grid-wrapper grid-wrapper--flush map map--episode map--count-2'})

            episode_longest_synopsis = main_episode_info.find(
                'div', attrs={'class': 'text--prose longest-synopsis'})
            if episode_longest_synopsis is not None:
                episode_longest_synopsis = episode_longest_synopsis.find_all('p')
                episode_longest_synopsis = ' '.join(
                    [x.get_text() for x in episode_longest_synopsis])
                episode_dict['episode'].update({'long_synopsis': episode_longest_synopsis})

            series_id = main_episode_info.find('div', attrs={'class': 'offset'})

            if series_id is not None:
                series_id_name = series_id.find_all('a')
                series_id = series_id_name[-1]['href']
                episode_dict['episode'].update({'series_id': series_id.split('/')[-1]})
                series_name = series_id_name[-1].get_text()
                episode_dict['episode'].update({'series_name': series_name})

            left_to_watch_dict = self.get_left_to_watch(episode_web_page)
            # this needs refactoring into a METHOD
            if left_to_watch_dict is not None:
                episode_dict['episode'].update(left_to_watch_dict)

            '''
            TODO: drill down from each of these main tag containers to get the info needed
            in the code below need to get next on if available last on, credits, credits, episode music
            supporting items ie podcast information and enrichers, and the genre.
            '''

            # Last on next on section
            last_on_next_on = episode_web_page.find(
                'div', attrs={'class': 'grid 1/3@bpw2 1/3@bpe map__column map__column--2 map__column--last'})

            last_on = last_on_next_on.find(
                'div', attrs={'data-map-column': 'tx', 'class': 'br-box-secondary'})

            last_broadcast = self.get_last_on(last_on)
            episode_dict['episode'].update({'broadcast': {'last_on': last_broadcast}})

            # role credits and music credits also contains featured in - for boxsets ie soaps
            credits_box = episode_web_page.find(
                'div', attrs={'class': 'grid grid--bounded 13/24@bpw2 13/24@bpe'})

            credits_dict = self.get_episode_credits(credits_box)
            episode_dict['episode'].update({"credits": credits_dict})

            music_played = self.get_episode_music(credits_box)
            episode_dict['episode'].update({'music': music_played})

            # promo and supporting material
            supporting_items = episode_web_page.find(
                'div', attrs={'class': 'grid grid--bounded 11/24@bpw2 11/24@bpe'})

            supporting_items_dict = self.get_episode_supportingitems(supporting_items)
            episode_dict['episode'].update({'supporting_content': supporting_items_dict})

            genres, formats = self.get_genre(episode_web_page)
            episode_dict['episode'].update({'genre': genres, 'format': formats})

            featured_in_dict = self.get_featured_in(episode_web_page)
            episode_dict['episode'].update({'collection': featured_in_dict})

            episode_broadcasts = self.get_boadcast_info(episode_web_page)
            episode_dict['episode']['broadcast'].update({'previous_broadcasts': episode_broadcasts})

            episodes_list.append(episode_dict)

        self.dictionary.add('episodes', {'available': episodes_list})

        return episodes_list

    # TODO navigate to the episode page & scrape
    def upcoming_episodes(self, url):
        '''next_on_suffix = 'broadcasts/upcoming/'''
        web_page = self.Browser.get_page(self._BASE_URL + url)

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

                microsite_info = self.episode_microsite_extractor(program_link, upcoming=True)

                temp_dict = {
                    'id': program_id.strip(),
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
                temp_dict.update(microsite_info)

                next_up.append(temp_dict)
            self.dictionary.update('episodes', {'next_up': next_up})
            return next_up

    def get_episode_credits(self, web_page):

        credits_table = web_page.find(
            'table', attrs={'class': 'table table--slatted-vertical no-margin-vertical'})

        if credits_table:
            credits_dict = {}
            for row in credits_table.find_all('tr'):
                person = row.find_all('span')
                if len(person) > 1:
                    json_credits = [x.get_text() for x in person]
                    credits_dict[json_credits[0]] = json_credits[1]
            return credits_dict
        else:
            return None

    def get_episode_music(self, web_page):

        music_location = web_page.find(
            'div',
            attrs={
                'class':
                'component component--box component--box-flushbody-vertical component--box--primary',
                'id': 'segments'})
        if music_location is not None:
            music_list = music_location.find(
                'ul', attrs={'class': 'list-unstyled segments-list__items'})

            if music_list is not None:
                music_dict = []

                for music in music_list.find_all('li'):
                    info = music.find('div', attrs={'class': 'segment__track'})
                    time_stamp = info.find(
                        'div', attrs={'class': 'text--subtle pull--right-spaced'})['aria-label']
                    artist = info.find('h3', attrs={'class': 'gamma no-margin'})

                    artist_url = artist.a['href'] if artist.a is not None else None

                    artist = artist.find('span', attrs={'class': 'artist'}).get_text()
                    track = info.find('p', attrs={'class': 'no-margin'}).get_text()
                    music_dict.append({'artist': artist,
                                       'artist_url': artist_url,
                                       'track': track,
                                       'time_stamp': time_stamp})
                return music_dict
            else:
                return None
        else:
            return None

    def get_boadcast_info(self, web_page):
        broadcast_info = web_page.find(
            'div', attrs={'class': 'component component--box component--box--primary', 'id': 'broadcasts'})
        if broadcast_info is not None:
            broadcast_list = broadcast_info.find(
                'ul', attrs={'class': 'grid-wrapper highlight-box-wrapper--grid'})
            broadcasts = []

            for item in broadcast_list.find_all('li'):
                broadcast = item.find('div', attrs={'class': 'broadcast-event__time beta'})

                time_stamp = broadcast['content']
                standard_date = broadcast['title']
                time = broadcast.find('span', attrs={'class': 'timezone--time'}).get_text()

                channel = item.find(
                    'div',
                    attrs={'class': 'programme__service box-link__elevated micro text--subtle'})
                channel_name = channel.get_text()
                broadcasts.append({'channel': channel_name,
                                   'time_stamp': time_stamp,
                                   'standard_date': standard_date,
                                   'time': time})
            return broadcasts
        else:
            return None

    def get_featured_in(self, web_page):

        featured_in = web_page.find('div', attrs={
                                    'class': 'component component--box component--box-flushbody component--box--primary', 'id': 'collections'})
        if featured_in is not None:
            featured_list = featured_in.find('ul', attrs={'class': 'list-unstyled'})

            featured_in_dict = []

            for item in featured_list.find_all('li'):
                item_info = item.find('a', attrs={'class': 'br-blocklink__link block-link__target'})
                title = item_info.find('span').get_text()
                subtitle = item.find('p').get_text()
                link = item_info['href']
                featured_in_dict.append({'title': title,
                                         'subtitle': subtitle,
                                         'link': link})
            return featured_in_dict
        else:
            return None

    # TODO: if none then omit
    def get_episode_supportingitems(self, web_page):
        '''extracts all elements from episode supporting contents

        Arguments:
            web_page {soup div tag} -- html content
        '''
        supporting_items = []
        content_list = web_page.find_all('div', recursive=False)
        for content in content_list:

            title = content.find('h2').get_text()

            link = content.find('a', attrs={'class': 'superpromo__img'})
            link = link['href'] if link is not None else None

            summary = content.find('div', attrs={'class': 'superpromo__content'})
            summary = summary.find('p').get_text() if summary is not None else None

            supporting_items.append({'title': title,
                                     'link': link,
                                     'summary': summary})

        return supporting_items

    def get_last_on(self, web_page):

        last_on = web_page.find('div', attrs={'class': 'broadcast-event__time beta'})
        date_time = last_on['content']
        standard_date = last_on['title']
        time = last_on.find('span', attrs={'class': 'timezone--time'})
        time = time.get_text()

        channel = web_page.find(
            'div', attrs={'class': 'programme__service box-link__elevated micro text--subtle'})
        channel_name = channel.get_text()

        return {'channel': channel_name,
                'date_tiem': date_time,
                'standard_date': standard_date,
                'time': time}

    def get_left_to_watch(self, web_page):

        left_to_watch = web_page.find(
            'div', attrs={'class': 'grid 1/3@bpw 1/4@bpe'})

        # TODO: something is breaking here
        if left_to_watch is not None:

            left_to_watch_list = left_to_watch.find_all('p', attrs={'class': 'episode-panel__meta'})
            days_left = left_to_watch_list[0].find('span')
            if days_left is not None:
                removal_date = days_left['title'] if days_left is not None else None
                days_left = days_left.get_text()
                duration = left_to_watch_list[1].get_text()
                return {'days_left': days_left, 'duration': duration, 'removal_date': removal_date}
        else:
            return None

    def extract_childrens(self, web_page):
        '''function to extract infomration from other page formats relating to cbeebies and cbbc

        Arguments:
            web_page {soup div tag} -- html content

        container for both related content and episode list content : div tag class : content-collection-sections__list
        separated into two list tags

        episodes    - id : episodes-container
                    - class: content-collection-sections__item content-collection-section content-collection-section--episodes pocket pocket--closed

                    follow link -> and then scrape:
                        container - gel-layout__item gel-1/2@xxl gel-7/12@l gel-8/12@m gel-1/1@xs
                            synopsis : synopsis typo typo--canary
                            duration first shown and available : inline-list episode-metadata typo--canary

        program availability - 'class; : 'programme-info__availability'
        extra content - 'class' : 'content-collection-page__sections


        if on program website div class : menu__product ['href] is /cbbc
        then use this function


        '''

        pass

    # TODO this needs rewriting asap - change to array output

    # def get_genre_format(self, web_page):
    #     genre_format = web_page.find(
    #         'div', attrs={'class': 'footer__similar b-g-p component'})

    #     if genre_format is None:
    #         genre_format = web_page.find(
    #             'div',
    #             attrs={
    #                 'class':
    #                 'islet--horizontal footer__programmes footer__service-island'
    #             })

    #     if genre_format is not None:
    #         sim = genre_format.find_all('div')
    #         genre_format_list = []

    #         for i in sim:
    #             genre_format_list.append([[x.get_text(), x['href']]
    #                                       for x in i.find_all('a', href=True)])

    #         genre_format_dict = {'genre': {}}

    #         # TODO this should be re-written into lists of dictionaries also handle multiple sub genres better

    #         for i in range(len(genre_format_list)):
    #             for j in range(len(genre_format_list[i])):
    #                 if i == 0:
    #                     if j < 1:
    #                         genre_format_dict['genre'].update({
    #                             'main': {
    #                                 str(j): genre_format_list[i][j][0],
    #                                 'link': genre_format_list[i][j][1]
    #                             }
    #                         })
    #                     elif j == 1:
    #                         genre_format_dict['genre'].update({
    #                             'sub_genre': {
    #                                 str(j): genre_format_list[i][j][0],
    #                                 'link': genre_format_list[i][j][1]
    #                             }
    #                         })
    #                     else:
    #                         genre_format_dict['genre']['sub_genre'].update({
    #                             str(j):
    #                             genre_format_list[i][j][0],
    #                             'link':
    #                             genre_format_list[i][j][1]
    #                         })
    #                 else:
    #                     if j < 1:
    #                         genre_format_dict.update({
    #                             'format': {
    #                                 str(j): genre_format_list[i][j][0],
    #                                 'link': genre_format_list[i][j][1]
    #                             }
    #                         })
    #                     else:
    #                         genre_format_dict['format'].update({
    #                             'sub_format': {
    #                                 str(j): genre_format_list[i][j][0],
    #                                 'link': genre_format_list[i][j][1]
    #                             }
    #                         })
    #         return genre_format_dict

    def episode_microsite_extractor(self, url, upcoming=False):
        '''function for extracting useful information form an episode microsite

        Arguments:
            url {url} -- should be a url to a bbc programme episode ie https://www.bbc.co.uk/programmes/m0002vlb

        Keyword Arguments:
            upcoming {bool} -- indicate whether the episode is upcoming or not to omit unuseful information (default: {False})

        Returns:
            dictionary of all useful information from episode webpage --  mainly for credits, series, and music information
         },
        '''

        episode_web_page = self.Browser.get_page(url)

        episode_dict = {}

        main_episode_info = episode_web_page.find(
            'div', attrs={'class': 'grid-wrapper grid-wrapper--flush map map--episode map--count-2'})

        episode_longest_synopsis = main_episode_info.find(
            'div', attrs={'class': 'text--prose longest-synopsis'})
        if episode_longest_synopsis is not None:
            episode_longest_synopsis = episode_longest_synopsis.find_all('p')
            episode_longest_synopsis = ' '.join([x.get_text() for x in episode_longest_synopsis])
            episode_dict.update({'long_synopsis': episode_longest_synopsis})

        series_id = main_episode_info.find('div', attrs={'class': 'offset'})

        if series_id is not None:
            series_id_name = series_id.find_all('a')
            series_id = series_id_name[-1]['href']
            episode_dict.update({'series_id': series_id.split('/')[-1]})
            series_name = series_id_name[-1].get_text()
            episode_dict.update({'series_name': series_name})

        if upcoming is False:
            left_to_watch_dict = self.get_left_to_watch(episode_web_page)
            # this needs refactoring into a METHOD
            if left_to_watch_dict is not None:
                episode_dict.update(left_to_watch_dict)

            episode_broadcasts = self.get_boadcast_info(episode_web_page)
            episode_dict.update({'previous_broadcasts': episode_broadcasts})

            # Last on next on section
            last_on_next_on = episode_web_page.find(
                'div', attrs={'class': 'grid 1/3@bpw2 1/3@bpe map__column map__column--2 map__column--last'})

            last_on = last_on_next_on.find(
                'div', attrs={'data-map-column': 'tx', 'class': 'br-box-secondary'})

            if last_on is not None:
                last_broadcast = self.get_last_on(last_on)

                episode_dict.update({'broadcast': {'last_on': last_broadcast}})

        # role credits and music credits also contains featured in - for boxsets ie soaps
        credits_box = episode_web_page.find(
            'div', attrs={'class': 'grid grid--bounded 13/24@bpw2 13/24@bpe'})

        credits_dict = self.get_episode_credits(credits_box)
        episode_dict.update({"credits": credits_dict})

        music_played = self.get_episode_music(credits_box)
        episode_dict.update({'music': music_played})

        # promo and supporting material
        supporting_items = episode_web_page.find(
            'div', attrs={'class': 'grid grid--bounded 11/24@bpw2 11/24@bpe'})
        if supporting_items is not None:
            supporting_items_dict = self.get_episode_supportingitems(supporting_items)
            episode_dict.update({'supporting_content': supporting_items_dict})

        genres, formats = self.get_genre(episode_web_page)
        episode_dict.update({'genre': genres, 'format': formats})

        featured_in_dict = self.get_featured_in(episode_web_page)
        episode_dict.update({'collection': featured_in_dict})

        return episode_dict

    def get_genre(self, web_page):
        '''takes web page and returns the genre and if applicable format of the episode/programme

        Arguments:
            web_page {soup html} -- html content relating to the program/episode microsite

        potential genre locations
        'grid grid--flush 1/2@bpw 1/4@bpw2 1/4@bpe' - episode microsite
        grid__item 1/3@gel4 1/4@gel3b 1/2@gel3 - program microsite

        '''

        # this will extract genre/format from programme microsite
        genre_format = web_page.find(
            'div', attrs={'class': 'grid__item 1/3@gel4 1/4@gel3b 1/2@gel3'})

        # this will extract genre format from the episode microsite
        if genre_format is None:
            genre_format = web_page.find(
                'div', attrs={'class': 'grid grid--flush 1/2@bpw 1/4@bpw2 1/4@bpe'})

        # extractor if episode microsite

        container = genre_format.find('div', attrs={'class': 'footer__similar b-g-p component'})
        if container is None:
            container = genre_format.find(
                'div', attrs={'class': 'islet--horizontal footer__programmes footer__service-island'})

        if container is not None:
            items = container.find_all('div')

            genres = []
            formats = []

            for item in items:

                for sub_item in item.find_all('li'):

                    link = sub_item.find_all('a')
                    for a in link:
                        if 'genres' in a['href']:
                            if len(genres) is 0:
                                genres.append({'genre': a.get_text(), 'link': a['href']})
                            else:
                                if a['href'] != genres[0]['link']:
                                    genres.append({'sub_genre': a.get_text(), 'link': a['href']})
                        elif 'formats' in a['href']:
                            if len(formats) is 0:
                                formats.append({'format': a.get_text(), 'link': a['href']})
                            else:
                                if a['href'] != formats[0]['link']:
                                    formats.append({'sub_format': a.get_text(), 'link': a['href']})

            return genres, formats
        else:
            return None, None
