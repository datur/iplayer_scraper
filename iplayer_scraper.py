# iplayer scraper

import mechanicalsoup
import json
import hashlib
from bs4 import BeautifulSoup
import sys

BASE_URL = 'https://www.bbc.co.uk/'

SCRAPING_SUFFIX = 'iplayer/a-z/'

browser = mechanicalsoup.StatefulBrowser()

browser.open(BASE_URL + SCRAPING_SUFFIX)

selection = browser.get_current_page().find_all(
    'li', attrs={"class": "grid__item"})

# titles = list-content-item__title
# synopsis = list-content-item__synopsis

# scrollable-nav__track -- is where the links to each letter are
'''
tab typo typo--canary atoz-nav__item typo typo--bold typo--bullfinch typo--bold tab--active
this is the list of attrs for link to alphabet
'''

program_data = {}

for item in selection:
    '''
    From the initial wep page with the list of programs collect the title
    and synopsis. Can also grab the number of episodes. Collect link for
    further extraction

    This section yields:

        Title
        Synopsis
        Episode Link

    '''

    title = item.find('p', attrs={"class": "list-content-item__title"})
    synopsis = item.find('p', attrs={'class': 'list-content-item__synopsis'})
    num_episodes_available = item.find(
        'div', attrs={'class': 'list-content-item__sublabels'})
    link = item.find('a', href=True)['href']

    print(link)
    '''
    Navigate to the episode page. From here credits and other information
    about show time can be extracted. .

    This section yields:

        Credits
        Genre
        Format


    get prog-layout programmes-page -> broadcast and credits
    synopsis-toggle__long -> longerform synopsis
    synopsis-toggle__short -> short synopsis
    component component--box component--box--primary -> brodcast
    information
    br-box-secondary -> secondary broadcast

    related_links -> <div> id |
        class = component component--box component--box--striped
                component--box--secondary


    '''

    browser.open(BASE_URL + link)

    # page
    page = browser.get_current_page()

    episode_page_url = page.find('a', attrs={'class': 'lnk'}, text='Credits')
    if episode_page_url is None:
        episode_page_url = browser.get_current_page().find(
            'a', attrs={'class': 'lnk'}, text='Programme website')
    print(episode_page_url['href'])

    browser.open(BASE_URL + episode_page_url['href'])

    # TODO: reassign the page to save on browser use.

    credits = browser.get_current_page().find(
        'table', attrs={'class': 'table'})

    if credits is not None:
        for row in credits.find_all('tr'):
            person = row.find_all('span')
            json_credits = [x.get_text() for x in person]
            print(json_credits)
    '''


    Section for finding similar shows
    '''
    similar = browser.get_current_page().find(
        'div', attrs={'class': 'footer__similar b-g-p component'})

    if similar is not None:
        sim = similar.find_all('div')
        genre_format = []

        for i in sim:
            genre_format.append(
                [[x.get_text(), x['href']] for x in i.find_all('a')])

        # Messy but works
        genre = []
        prog_frmat = []

        for i in range(len(genre_format)):
            for j in range(len(genre_format[i])):
                #print(genre_format[i][j])
                if i == 0:
                    genre.append(genre_format[i][j])
                else:
                    prog_frmat.append(genre_format[i][j])

        print(genre)
        print(prog_frmat)
    '''


    Section for Duration and left to watch


    '''
    left_to_watch = browser.get_current_page().find(
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

        print('Left to watch:', days_left, duration)
    '''


    section for longer synopsis


    '''
    long_synopsis = browser.get_current_page().find(
        'div', attrs={'class': 'synopsis-toggle__long'})

    if long_synopsis is not None:
        long_synopsis_paragraphs = [
            x.get_text() for x in long_synopsis.find_all('p')
        ]

        print(long_synopsis_paragraphs)

    # Broadcast information:

    main_broadcast = browser.get_current_page().find(
        'div',
        attrs={
            'class':
            'grid 1/3@bpw2 1/3@bpe map__column map__column--2 map__column--last'
        })

    if main_broadcast is not None:
        date_last_aired = main_broadcast.find(
            'span',
            attrs={'class': 'broadcast-event__date text-base timezone--date'})
        time_last_aired = main_broadcast.find(
            'span', attrs={'class': 'timezone--time'})
        channel = main_broadcast.find(
            'div',
            attrs={
                'class':
                'programme__service box-link__elevated micro text--subtle'
            })
        if channel is not None:
            channel_text = channel.find('a').get_text()
        if channel is not None:
            channel_link = channel.find('a')['href']
        if date_last_aired is not None:
            date_last_aired = date_last_aired.get_text()
        if time_last_aired is not None:
            time_last_aired = time_last_aired.get_text()

        print('date:', date_last_aired, 'Time:', time_last_aired, 'Channel:',
              channel_text, channel_link)
    '''


    section for extra links

    You may also like
        footer__recommendations br-keyline lazy-module--complete

    other available episodes

    <a class="br-nav__link" href="/programmes/b0bxbvtl/episodes" data-linktrack="nav_episodes">Episodes</a>


    '''

    episodes_link = browser.get_current_page().find(
        'a', attrs={
            'class': 'br-nav__link',
            'data-linktrack': 'nav_episodes'
        })

    if episodes_link is not None:
        episodes_link = episodes_link['href']

    print(episodes_link)
    '''
    TODO: navigate to episodes link

    if episodes is none then skip

    br-box-page programmes-page -> div html class containing the available episodes

    within the list of program list:

    loop through each div with class programme programme--tv programme--episode block-link highlight-box--list br-keyline br-blocklink-page br-page-linkhover-onbg015--hover
     in ol class highlight-box-wrapper

    find abbr
    find a with class br-blocklink__link block-link__target
    find span with class  programme__title gamma
    find span with programme__subtitle centi
    find p with programme__synopsis text--subtle centi



    '''
    if episodes_link is not None:

        browser.open(BASE_URL + episodes_link)

        episodes_page = browser.get_current_page()

        episodes_available_list = episodes_page.find(
            'div', attrs={'class': 'br-box-page programmes-page'})

        episodes_container_list = episodes_available_list.find_all(
            'div',
            attrs={
                'class':
                'programme programme--tv programme--episode block-link highlight-box--list br-keyline br-blocklink-page br-page-linkhover-onbg015--hover'
            })

        print(episodes_container_list)

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
                    something = (item_body.p.span.get_text())
                    somethin1 = (item_body.p.abbr['title'])

                    print(
                        item_body.find(
                            'span',
                            attrs={
                                'class': 'programme__subtitle centi'
                            }).get_text())

                except:
                    print('not availbale')

    # broadcast = browser.get_current_page().find(
    #     'div',
    #     attrs={'class': 'component component--box component--box--primary'})

    # broadcast_secondary = browser.get_current_page().find(
    #     'div', attrs={'class': 'br-box-secondary'})

    # if broadcast is not None:
    #     channel = broadcast.find(
    #         'div',
    #         attrs={
    #             'class':
    #             'programme__service box-link__elevated micro text--subtle'
    #         })

    #     print(channel.find('a'))

    # # Try secondary broadcast location

    # if broadcast_secondary is not None:
    #     secondary_channel = broadcast_secondary.find(
    #         'div',
    #         attrs={
    #             'class':
    #             'programme__service box-link__elevated micro text--subtle'
    #         })
    #     print(secondary_channel)
