from selenium import webdriver
from multiprocessing import Pool, cpu_count, Lock, active_children, current_process, Manager
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import io
import json
import sys
from tqdm import tqdm
import time
from multiprocessing import Queue, Process
from itertools import repeat


def main():

    url = "http://bbc.co.uk/iplayer/a-z"

    browser = get_driver()

    manager = Manager()

    shared_dict = manager.dict()
    shared_list = manager.list()

    get_page(browser, url)
    html = browser.execute_script("return document.body.innerHTML")
    html = BeautifulSoup(html, 'lxml')

    

    atoz = html.find('div', attrs={'class': "atoz-nav__inner"})
    navigation = atoz.find('ul', attrs={'class': 'scrollable-nav__track'})
    navigation_list = navigation.find_all('li')
    navigation_list = [
        x.a['href'] for x in navigation_list if x.a is not None
    ]

    browser.quit

    print(cpu_count())

    # processes = [Process(target=run_programme_extraction_per_char, args=(x, shared_list)) for x in navigation_list]
    # active = []

    # with Manager() as manager:
    #     for p in processes:
    #         p.start()
    #         active.append(p)

    #     for p in active:
    #         p.join()

    


    # for p in processes:
    #     p.start()
    #     active.append(p)
    #     print(len(active_children()))

    #     while len(active_children()) >= (cpu_count()-2):
    #         for task in active:
    #             print(f"active task: {task} {'Task is alive' if task.is_alive() else 'Task Complete'}")
    #         # if _FINISH:
    #         #     p.join()
    #         print(f"current processes: {len(active_children())}. Waiting for execution slot \n")
    #         time.sleep(10)

    # for p in processes:
    #      p.start()

    # for p in processes:
    #      p.join()

    with Pool(cpu_count()-2) as p:
        p.starmap(run_programme_extraction_per_char, zip(navigation_list, repeat(shared_list)))
    p.close()
    p.join()

    results=[item for item in shared_list]

    print(results)
    print('finished')


def get_driver():
    options=Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument('--disable-logging')
    # initialize driver
    driver=webdriver.Chrome(options = options)
    return driver


def get_page(browser, url):
    time.sleep(10)
    try:
        browser.get(url)

    except:
        print(f'browser: {url} failed to load')


def run_programme_extraction_per_char(suffix, shared_list):

    #print(suffix.split('/')[-1])

    browser=get_driver()
    url=f'http://bbc.co.uk{suffix}'

    get_page(browser, url)
    html=browser.execute_script("return document.body.innerHTML")
    html=BeautifulSoup(html, 'lxml')

    if html is not None:
        # find each programme box
        programme_selection=html.find_all(
            'li', attrs = {"class": "grid__item"})

        # for each programme box
        for programme_box in tqdm(programme_selection):

            dictionary={}

            programme_box_json=parse_programme_box(programme_box)
            dictionary.update(programme_box_json)
            # get and extract initial programme page
            # programme_microsite_url=parse_latest_episode(
            #     browser, programme_box_json['latest_episode_url'])
            # if programme_microsite_url is not None:
            #     programme_microsite_json=parse_programme_microsite(
            #         browser, programme_microsite_url)
            #     dictionary.update(programme_microsite_json)

            shared_list.append(dictionary)

    browser.quit()


def run_programme_extraction_per_programme(programme_box, filename):
    pass


def parse_programme_box(programme_box):

    programme_box_dict={}

    title=programme_box.find(
        'p', attrs={'class': 'list-content-item__title'})

    if title is not None:
        title = title.get_text()
        programme_box_dict.update({'title': title})
        # (title)
    else:
        title = programme_box.find(
            'div', attrs={'class': 'content-item__title'})
        if title is not None:
            title = title.get_text()
            programme_box_dict.update({'title': title})

    # Program Synopsis
    synopsis = programme_box.find(
        'p', attrs={'class': 'list-content-item__synopsis'})

    if synopsis is not None:
        synopsis = synopsis.get_text()
        programme_box_dict.update({'synopsis': synopsis})
    else:
        synopsis = programme_box.find(
            'div', attrs={'class': 'content-item__description'})
        if synopsis is not None:
            synopsis = synopsis.get_text()
            programme_box_dict.update({'synopsis': synopsis})

    # Link to latest episode
    latest_episode_url = programme_box.find('a', href=True)['href']
    programme_box_dict.update({'latest_episode_url': latest_episode_url})

    # Number of episodes available
    episodes_available = programme_box.find(
        'div', attrs={'class': 'list-content-item__sublabels'})

    if episodes_available is not None:
        episodes_available = episodes_available.get_text()
        programme_box_dict.update({'episodes_available': episodes_available})

    return programme_box_dict


def parse_pogramme(browser, url):
    '''main parser method

    Arguments:
        browser {selenium web driver}
        url {url} -- formatted url relating to a bbc iplayer programme
    '''

    pass


def parse_latest_episode(browser, url):
    '''helper method to extract the programme microsite url
    from the latest episode.

    Arguments:
        browser {selenium web driver} -- tested working with chrome
        url {url} -- latest programme episode url
    '''
    get_page(browser, 'http://bbc.co.uk' + url)

    html = browser.execute_script("return document.body.innerHTML")

    html = BeautifulSoup(html, 'lxml')

    if html is not None:
        program_website_url = html.find(
            'a', attrs={'class': 'lnk'}, text='Programme website')
    else:
        print('\n\n\n', url, '\n\n\n')

    if program_website_url:
        program_website_url = program_website_url['href']

    return program_website_url


def parse_programme_microsite(browser, url):
    '''parse and extract all useful informqtion from a programme on
    the bbc iplayer.

    Arguments:
        browser {selenium web driver}
        url {url} -- should be a link to a bbc iplayer programme
    '''
    dictionary = {}
    get_page(browser, 'http://bbc.co.uk' + url)

    html = browser.execute_script("return document.body.innerHTML")

    html = BeautifulSoup(html, 'lxml')

    channel_check = html.find('div', attrs={'class': 'menu__bar'})

    if channel_check is not None:
        channel = channel_check.find('a', attrs={'class': 'menu__product'})

        if channel['href'] == '/cbbc' or channel['href'] == '/cbeebies':
            # print(program_website_url)
            extract_childrens(browser, html)
    else:
        genres, formats = get_genre(html)
        dictionary.update({'genre': genres})
        if format is not {}:
            dictionary.update({'format': formats})

        try:
            synopsis = programme_synopsis(html)
            dictionary.update({'synopsis': synopsis})

        except Exception as e:
            print('Error ', e, ' at:', url)

        supporting_content_dict = supporting_content(html)
        dictionary.update({'supporting_content': supporting_content_dict})

        recommendation_dictionary = full_recommend(
            browser, 'http://bbc.co.uk' + url + '/recommendations')
        dictionary.update({'recommendations': recommendation_dictionary})

        episodes(browser, html)

    return dictionary


def episodes(browser, html):

    episodes_link = html.find(
        'a',
        attrs={
            'class': 'br-nav__link',
            'data-linktrack': 'nav_episodes'
        })

    if episodes_link is not None:

        episodes_link = episodes_link['href']

        # debug
        # print(episodes_link)

        get_page(browser, 'http://bbc.co.uk' + episodes_link)

        html_base = browser.execute_script("return document.body.innerHTML")

        html_base = BeautifulSoup(html_base, 'lxml')

        episodes_available = []
        episodes_available.append(episode_list_extractor(browser, html))

        episode_pagination = html_base.find(
            'ol', attrs={'class': 'nav nav--banner pagination delta'})

        if episode_pagination:
            page_list = episode_pagination.find_all(
                'li', attrs={'class': 'pagination__page'})
            page_links = [
                x.a['href'] for x in page_list if x.a is not None
            ]

            for endpoint in page_links:
                url = 'http://bbc.co.uk' + episodes_link + endpoint

                get_page(browser, url)

                html = browser.execute_script("return document.body.innerHTML")

                html = BeautifulSoup(html, 'lxml')

                episodes_available.append(episode_list_extractor(browser, html))

        next_on = html_base.find(
            'ul', attrs={
                'class': 'list-unstyled cf delta'
            }).find_all('li')

        if next_on[-1].a:
            episodes_upcoming = upcoming_episodes(browser, 'http://bbc.co.uk'+next_on[-1].a['href'])
            episodes_available.append(episodes_upcoming)


def upcoming_episodes(browser, url):
    '''next_on_suffix = 'broadcasts/upcoming/'''
    dictionary = {}

    get_page(browser, url)

    html = browser.execute_script("return document.body.innerHTML")

    html = BeautifulSoup(html, 'lxml')

    next_on_section = html.find(
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

            microsite_info = episode_microsite_extractor(browser, program_link, upcoming=True)

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
        dictionary.update({'episodes': {'next_up': next_up}})
    return next_up


def full_recommend(browser, url):
    '''if available the bbc iplayer recommendations for a program will be extracted

    Arguments:
        url {string of a url} -- this should be suffixed with '/recommendations'
    '''

    dictionary = {}

    get_page(browser, url)

    html = browser.execute_script("return document.body.innerHTML")

    html = BeautifulSoup(html, 'lxml')

    if html is not None:
        page_items = html.find(
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
                episode_microsite = episode_microsite_extractor(browser, 'http://bbc.co.uk' + link)

                tmp_dict.update({
                    'id': _id,
                    'title': title,
                    'synopsis': synop,
                    'link': link
                })
                tmp_dict.update(episode_microsite)
                recommendations.append(tmp_dict)
            dictionary.update({'recommendations': recommendations})
    return dictionary


def supporting_content(web_page_element):
    '''will look for supporting content in the given webpage

    Arguments:
        web_page_element {beautifuloup element} -- should be related to a programme microsite
    '''

    dictionary = {}

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
        dictionary.update({'supporting_content': supporting_content_collection})
    return dictionary


def extract_childrens(browser, web_page):
    programme_dict = {}

    programme_details = web_page.find('div', attrs={'class': 'programme-info__details'})

    if programme_details == None:
        print('web_page: ', web_page)

    programme_synopsis = programme_details.find(
        'p', attrs={'class': 'programme-info__description'})

    programme_title = programme_details.find('h2', attrs={'class': 'programme-info__title'})

    program_availability = web_page.find('div', attrs={'class': 'programme-info__availability'})

    tv_availability = program_availability.find('div', attrs={'class': 'programme-schedule-info'})

    if tv_availability is not None:
        broadcast_info = tv_availability.find(
            'div', attrs={'class': 'programme-schedule-info__info'})
        broadcast_day = broadcast_info.find('p', attrs={'class': 'programme-schedule-info__day'})
        broadcast_time = broadcast_info.find('p', attrs={'class': 'programme-schedule-info__time'})
        broadcast_channel = broadcast_info.find(
            'p', attrs={'class': 'programme-schedule-info__product-name'})
        programme_dict.update({'broadcast': {'broadcast_day': broadcast_day.get_text(),
                                             'broadcast_time': broadcast_time.get_text(),
                                             'broadcast_channel': broadcast_channel.get_text()}})
    else:
        broadcast_info = "online only"

    programme_dict.update({'programme_title': programme_title.get_text(),
                           'programme_synopsis': programme_synopsis.get_text()})

    supporting_content_location = web_page.find(
        'ul', attrs={'class': 'content-collection-sections__list'})

    supporting_content = supporting_content_location.find(
        'div',
        attrs={
            'data-stats-children-index': '',
            'id': 'all-container'})

    if supporting_content is not None:
        supporting_list = supporting_content.find('ul', attrs={'class': 'content-list'})

        supporting_items = []

        for content in supporting_list.find_all('li', attrs={'class': 'content-list__item'}):
            link_details = content.find('a')
            if link_details is None:
                print(content)
            link = link_details['href']

            content_type = link_details['data-site-section']
            description = content.find('p', attrs={'class': 'content-card__title'})
            supporting_items.append({'link': link,
                                     'content_type': content_type,
                                     'description': description['aria-label']})

        programme_dict.update({'supporting_content': supporting_items})

    episode_content = supporting_content_location.find(
        'div',
        attrs={
            'id': 'episodes-container',
            'data-stats-children-index': 'episodes'})

    if episode_content is not None:

        episode_list = episode_content.find('ul', attrs={'class': 'content-list'}).find_all('li')

        episode_items = []

        for content in episode_list:

            temp_dict = {}

            link_details = content.find('a')
            link = link_details['href']

            _id = link.split('/')[-1] if link.split('/')[-1] is not "ad" else link.split('/')[-2]
            # print(_id)

            content_type = link_details['data-site-section']

            episode_title = content.find('p', attrs={'class': 'content-card__title'})['aria-label']

            temp_dict.update({'id': _id,
                              'link': link,
                              'content_type': content_type,
                              'episode_title': episode_title})

            get_page(browser, link)

            html = browser.execute_script("return document.body.innerHTML")

            episode_html = BeautifulSoup(html, 'lxml')

            title_location = episode_html.find(
                'div', attrs={'class': 'play-cta__text js-play-cta-text play-cta__text--with-subtitle'})
            if title_location is not None:
                title = title_location.find(
                    'span', attrs={'class': 'typo typo--buzzard typo--bold play-cta__text__title'})
                title = title.get_text()

                series_titles = title_location.find(
                    'span', attrs={'class': 'typo typo--skylark play-cta__text__subtitle'})
                series_titles = series_titles.get_text()

            synopsis = episode_html.find('p', attrs={'class': 'synopsis__paragraph'})
            synopsis = synopsis.get_text() if synopsis is not None else None

            temp_dict.update({'title': title,
                              'series': series_titles,
                              'synopsis': synopsis})

            metadata = episode_html.find(
                'ul', attrs={'class': 'inline-list episode-metadata typo--canary'})
            if metadata is not None:
                for item in metadata.find_all('li', attrs={'class': 'inline-list__item'}):
                    item_type = item.find('span', attrs={'class': 'tvip-hide'})

                    if item_type is not None and item_type.get_text() == 'Duration':
                        duration = item.find('span', attrs={'class': 'episode-metadata__text'})
                        duration = duration.get_text()
                        temp_dict.update({'duration': duration})

                    if item_type is not None and item_type.get_text() == 'First shown':
                        first_shown = item.find('span', attrs={'class': 'episode-metadata__text'})
                        first_shown = first_shown.get_text()
                        temp_dict.update({'first_shown': first_shown})

                    if item.span is not None:
                        if 'Available' in item.span:
                            available_until = item.find(
                                'span', attrs={'class': 'episode-metadata__text'})
                            available_until = available_until.get_text()
                            temp_dict.update({'available_until': available_until})

                episode_items.append(temp_dict)

        programme_dict.update({'episodes': episode_items})

    return programme_dict


def write_file(file_name, payload):
    with open(file_name, 'a+') as f:
        json.dump(payload, f)
        f.write('\n')


def get_genre(web_page):
    genre_format = web_page.find(
        'div', attrs={'class': 'grid__item 1/3@gel4 1/4@gel3b 1/2@gel3'})

    # this will extract genre format from the episode microsite
    if genre_format is None:
        genre_format = web_page.find(
            'div', attrs={'class': 'grid grid--flush 1/2@bpw 1/4@bpw2 1/4@bpe'})

    # extractor if episode microsite
    if genre_format is not None:

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
    else:
        return None, None


def programme_synopsis(html):

    dictionary = {}

    long_synopsis = html.find(
        'div', attrs={'class': 'text--prose longest-synopsis'})

    if long_synopsis is None:
        long_synopsis = html.find(
            'div', attrs={'class': 'synopsis-toggle text--prose'})
        if long_synopsis is not None:
            long_synopsis = [x.get_text() for x in long_synopsis.find_all('p')]
            long_synopsis = ' '.join(long_synopsis) if long_synopsis is not None else None
            dictionary.update({'long_synopsis': long_synopsis})

    if long_synopsis is None:
        long_synopsis = html.find(
            'div', attrs={'class': 'programme-info__text-container'})
        if long_synopsis is not None:
            long_synopsis = long_synopsis.find(
                'p', attrs={'class': 'programme-info__description'})
            long_synopsis = long_synopsis.get_text() if long_synopsis is not None else None
            dictionary.update({'long_synopsis': long_synopsis})

    if long_synopsis is None:
        long_synopsis = html.find(
            'p', attrs={'class': 'gel-brevier media__meta-row'})
        if long_synopsis is not None:
            long_synopsis = long_synopsis.get_text() if long_synopsis is not None else None
            dictionary.update({'long_synopsis': long_synopsis})

    return dictionary


def episode_list_extractor(browser, web_page):
    episodes_list = []
    episodes_available_list = web_page.find(
        'ol', attrs={'class': 'highlight-box-wrapper'})
    if episodes_available_list is not None:
        episodes_container_list = episodes_available_list.find_all('div', recursive=False)

        

        for item in episodes_container_list:

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
            episode_time_left = episode_time_left.a['title'] if episode_time_left is not None else None
            episode_dict['episode'].update({'episode_time_left': episode_time_left})

            # TODO this should be refactored
            get_page(browser, episode_link)
            html = browser.execute_script("return document.body.innerHTML")

            html = BeautifulSoup(html, 'lxml')

            main_episode_info = html.find(
                'div', attrs={'class': 'grid-wrapper grid-wrapper--flush map map--episode map--count-2'})
            if main_episode_info is not None:
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

                left_to_watch_dict = get_left_to_watch(html)
                # this needs refactoring into a METHOD
                if left_to_watch_dict is not None:
                    episode_dict['episode'].update(left_to_watch_dict)

                '''
                    TODO: drill down from each of these main tag containers to get the info needed
                    in the code below need to get next on if available last on, credits, credits, episode music
                    supporting items ie podcast information and enrichers, and the genre.
                '''

                # Last on next on section
                last_on_next_on = html.find(
                    'div', attrs={'class': 'grid 1/3@bpw2 1/3@bpe map__column map__column--2 map__column--last'})

                last_on = last_on_next_on.find(
                    'div', attrs={'data-map-column': 'tx', 'class': 'br-box-secondary'})

                last_broadcast = get_last_on(last_on) if last_on is not None else None
                episode_dict['episode'].update({'broadcast': {'last_on': last_broadcast}})

                # role credits and music credits also contains featured in - for boxsets ie soaps
                credits_box = html.find(
                    'div', attrs={'class': 'grid grid--bounded 13/24@bpw2 13/24@bpe'})

                credits_dict = get_episode_credits(credits_box)
                episode_dict['episode'].update({"credits": credits_dict})

                music_played = get_episode_music(credits_box)
                episode_dict['episode'].update({'music': music_played})

                # promo and supporting material
                supporting_items = html.find(
                    'div', attrs={'class': 'grid grid--bounded 11/24@bpw2 11/24@bpe'})

                supporting_items_dict = get_episode_supportingitems(supporting_items)
                episode_dict['episode'].update({'supporting_content': supporting_items_dict})

                genres, formats = get_genre(html)
                episode_dict['episode'].update({'genre': genres, 'format': formats})

                featured_in_dict = get_featured_in(html)
                episode_dict['episode'].update({'collection': featured_in_dict})

                episode_broadcasts = get_boadcast_info(html)
                episode_dict['episode']['broadcast'].update({'previous_broadcasts': episode_broadcasts})

                episodes_list.append(episode_dict)
            else:
                print(browser.current_url)
        

    return episodes_list

def episode_microsite_extractor(browser, url, upcoming=False):
    '''function for extracting useful information form an episode microsite

    Arguments:
        url {url} -- should be a url to a bbc programme episode ie https://www.bbc.co.uk/programmes/m0002vlb

    Keyword Arguments:
        upcoming {bool} -- indicate whether the episode is upcoming or not to omit unuseful information (default: {False})

    Returns:
        dictionary of all useful information from episode webpage --  mainly for credits, series, and music information
        },
    '''

    get_page(browser, url)

    html = browser.execute_script("return document.body.innerHTML")

    html = BeautifulSoup(html, 'lxml')

    episode_dict = {}

    main_episode_info = html.find(
        'div', attrs={'class': 'grid-wrapper grid-wrapper--flush map map--episode map--count-2'})
    if main_episode_info is not None:
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
            episode_dict.update({'series_id': series_id.split('/')[-1] if series_id.split('/')[-1] is not "ad" else series_id.split('/')[-2] })
            series_name = series_id_name[-1].get_text()
            episode_dict.update({'series_name': series_name})

        if upcoming is False:
            left_to_watch_dict = get_left_to_watch(html)
            # this needs refactoring into a METHOD
            if left_to_watch_dict is not None:
                episode_dict.update(left_to_watch_dict)

            episode_broadcasts = get_boadcast_info(html)
            episode_dict.update({'previous_broadcasts': episode_broadcasts})

            # Last on next on section
            last_on_next_on = html.find(
                'div', attrs={'class': 'grid 1/3@bpw2 1/3@bpe map__column map__column--2 map__column--last'})

            last_on = last_on_next_on.find(
                'div', attrs={'data-map-column': 'tx', 'class': 'br-box-secondary'})

            if last_on is not None:
                last_broadcast = get_last_on(last_on)

                episode_dict.update({'broadcast': {'last_on': last_broadcast}})

    # role credits and music credits also contains featured in - for boxsets ie soaps
    credits_box = html.find(
        'div', attrs={'class': 'grid grid--bounded 13/24@bpw2 13/24@bpe'})
    if credits_box is not None:
        credits_dict = get_episode_credits(credits_box)
        episode_dict.update({"credits": credits_dict})

        music_played = get_episode_music(credits_box)
        episode_dict.update({'music': music_played})

    # promo and supporting material
    supporting_items = html.find(
        'div', attrs={'class': 'grid grid--bounded 11/24@bpw2 11/24@bpe'})
    if supporting_items is not None:
        supporting_items_dict = get_episode_supportingitems(supporting_items)
        episode_dict.update({'supporting_content': supporting_items_dict})

    genres, formats = get_genre(html)
    episode_dict.update({'genre': genres, 'format': formats})

    featured_in_dict = get_featured_in(html)
    episode_dict.update({'collection': featured_in_dict})

    return episode_dict

def get_left_to_watch(web_page):

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

def get_last_on(web_page):

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

def get_episode_credits(web_page):

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

def get_episode_music(web_page):
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
                if info is not None:
                    time_stamp = info.find(
                        'div', attrs={'class': 'text--subtle pull--right-spaced'})
                    time_stamp = time_stamp['aria-label'] if time_stamp is not None else None
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

def get_episode_supportingitems(web_page):
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

def get_featured_in(web_page):

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

def get_boadcast_info(web_page):
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

if __name__ == '__main__':
    main()
