#!/usr/bin/env python
# coding: utf-8

import mechanicalsoup
import json
import hashlib
from bs4 import BeautifulSoup
import sys

BASE_URL = 'https://www.bbc.co.uk'

SCRAPING_SUFFIX = '/iplayer/a-z/'

browser = mechanicalsoup.StatefulBrowser()

# Dictionary to hold the data

program_data = {}

browser.open(BASE_URL + SCRAPING_SUFFIX)

selection = browser.get_current_page().find_all(
    'li', attrs={"class": "grid__item"})

navigation = browser.get_current_page().find('ul', attrs={'class': 'scrollable-nav__track'})

navigation_list = navigation.find_all('li')

navigation_list = [x.a['href'] for x in navigation_list if x.a is not None ]

print(navigation_list)


# From the initial wep page with the list of programs collect the title and synopsis. Can also grab the number of episodes. Collect link for further extraction

for item in selection:
    title = item.find('p', attrs={"class": "list-content-item__title"})
    synopsis = item.find('p', attrs={'class': 'list-content-item__synopsis'})
    num_episodes_available = item.find(
        'div', attrs={'class': 'list-content-item__sublabels'})
    link = item.find('a', href=True)['href']
    print('link: ',link)
    print('title: ', title.get_text())
    print('synopsis: ', synopsis.get_text())
    
    
    '''
    Follow link for each program item
    '''
    
    browser.open(BASE_URL + link)
    page = browser.get_current_page()

    episode_page_url = page.find('a', attrs={'class': 'lnk'}, text='Credits')
    if episode_page_url is None:
        episode_page_url = browser.get_current_page().find(
            'a', attrs={'class': 'lnk'}, text='Programme website')
    print('latest_episode_url: ', episode_page_url['href'])
    
    
    # navigate to episode page
    browser.open(BASE_URL + episode_page_url['href'])
    episode_page = browser.get_current_page()
    credits = episode_page.find('table', attrs={'class': 'table'})
    
    credits_dict = {}
    if credits is not None:
        for row in credits.find_all('tr'):
            person = row.find_all('span')
            if len(person) > 1:
                json_credits = [x.get_text() for x in person]
                credits_dict[json_credits[0]] = json_credits[1]
        print(credits_dict)

        
    
    similar = episode_page.find(
        'div', attrs={'class': 'footer__similar b-g-p component'})

    if similar is not None:
        sim = similar.find_all('div')
        genre_format = []

        for i in sim:
            genre_format.append(
                [[x.get_text(), x['href']] for x in i.find_all('a')])

        genre_dict={}
        prog_frmt_dict = {}
        genre = []
        prog_frmat = []

        for i in range(len(genre_format)):
            for j in range(len(genre_format[i])):
                if i == 0:
                    genre.append(genre_format[i][j])
                else:
                    prog_frmat.append(genre_format[i][j])

        print('genre: ', genre)
        print('format: ',prog_frmat)


    left_to_watch = episode_page.find(
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

        print('Left to watch: ', days_left,'duration: ' ,duration)
    
    
    
    long_synopsis = episode_page.find(
        'div', attrs={'class': 'synopsis-toggle__long'})

    if long_synopsis is not None:
        long_synopsis_paragraphs = [
            x.get_text() for x in long_synopsis.find_all('p')
        ]

        print('long_synopsis: ',long_synopsis_paragraphs)

    # Broadcast information:

    main_broadcast = episode_page.find(
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

        print('date: ', date_last_aired, 'Time: ', time_last_aired, 'Channel: ',
              channel_text, channel_link)
        
    # you may also like
    # navigate to : current page + /recommendations
    # scrape the same way as getting other episode data
    
    current_url = browser.get_url()
    
    browser.open(current_url + '/recommendations')
    
    recommend_page = browser.get_current_page()
    
    if recommend_page is not None:
    
        page_items = recommend_page.find('ol', attrs={'class': 'highlight-box-wrapper'})
        
        if page_items is not None: 
            list_items = page_items.find_all('li')
            for item in list_items:
                item_info = item.find('div', attrs={'class': 'programme__body'})
                link_1 = item_info.h4.a['href']
                link_2 = item_info.h4.a['resource']
                title = item_info.h4.a.get_text()
                synop = item_info.p.get_text()
                
                print('recommendations:', link_1, link_2, 'title: ',title, synop)
    
    
    episodes_link = episode_page.find(
        'a', attrs={
            'class': 'br-nav__link',
            'data-linktrack': 'nav_episodes'
        })
    
    if episodes_link is not None:
        episodes_link = episodes_link['href']

        print(episodes_link)
    
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

        available_episodes = episodes_page.find('span', attrs={'class': 'hidden grid-visible@bpb2 grid-visible@bpw'})
        print('available episodes: ', available_episodes.get_text())
        
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
        
            print(item_link, item_time_left)
        
            if item_body is not None:
                # num of episodes
                try: 
                    episode_oneline_synopsis = item_body.p.get_text()
                    print('episode_oneline_synopsis: ' ,episode_oneline_synopsis)
                except:
                    pass
                try:
                    episode_no = item_body.p.abbr['title']
                    print('episode_no: ', episode_no)
                except:
                    pass
                try:
                    episode_title = item_body.find('span', attrs={'class': 'programme__title gamma'}).get_text()
                    print(episode_title)
                except:
                    pass
        
        episode_pagination = episode_page.find('ol', attrs={'class': 'nav nav--banner pagination delta'})
        
        print(episode_pagination)
       
    print('\n')


'''
Method to extract program information for the A to Z iplayer pages. This method will yield containing:

    - Program name
    - program id
    - program episode url 
    - small synopsis 

'''
def iplayer_atoz_page_extractor(program_selection):
    '''arguement is soup div tag for a program.
    Returns program title, program synopsis, no of
    episodes available, and the link to the latest episode'''
    # Program Title
    title = program_selection.find('p',
            attrs={'class':
                'list-content-item__title'}).get_text()
    # Program Synopsis
    synopsis = program_selection.find('p',
            attrs={'class':
                'list-content-item__synopsis'}).get_text()
    # Link to latest episode
    latest_episode_url = program_selection.find('a',
            href=True)['href']
    # Number of episodes available
    episodes_available = program_selection.find('div',
            attrs={'class': 'list-content-item__sublabels'})
    
    
    return title, synopsis, latest_episode_url


'''
method for extractingbasic information from each episode page. 
This method will yield containing:

    - latest episode name
    - long synopsis
    - duration 
    - broadcast date
    - broadcast channel
    - days left to watch
'''
def episode_page_extractor():
         

    return 0

'''

This method will yield:
    
    - program website url
    - bool of wether credits are available
'''
def programme_website_extractor(web_page):
    
    program_website_url = web_page.find('a',
            attrs={'class': 'lnk'},
            text='Programme website')['href']
    program_credits_url = web_page.find('a',
            attrs={'class': 'lnk'},
            text='Credits')
    
    credits_available = bool(program_credits_url)
    
    return program_website_url, credits_available

'''
Method for extracting a list of bbc recommended shows relating to the current program.

This method yields:

    - a list of programs containing
        - show name
        - show link
        - short synopsis
'''
def recommendation_extraction(browser):
    url = browser.get_url() + '/recommendations'
    browser.open(url)
    recommend_page = browser.get_current_page()

    return 0

'''
Method for extracting a list of available episodes of the current show.

this method yields:

    - number of available episodes
    - a list of available episodes containing
        - episode name
        - episode name
        - synopsis
    - if there are any upcoming episodes
        - a list of upcoming containing
            - title
            - series
            - synopsis
            - broadcast info
'''
def episode_list_extraction():
    
    return 0

'''
wrapper method to simplyfy browser navigation
'''
def navigate_to_url(browser, url):
    '''
    arguements: mechanicalsoup stateful browser object, url
    returns:    the html of the url navigated to
    '''
    browser.open(url)
    return browser.get_current_page() 

'''
Method for building the required dictionaries for each show

'''
def dictionary_builder():
    
    return 0

#testing

base_url = 'https://www.bbc.co.uk/programmes/b007y6k8/'
url = 'https://www.bbc.co.uk/programmes/b007y6k8/episodes/player'

def episode_pagination_test():
    episode_page = browser.get_current_page()
    pagination = episode_page.find('ol', attrs={'class': 'nav nav--banner pagination delta'})
    
    page_list = pagination.find_all('li', attrs={'class': 'pagination__page'})
    
    curr_url = browser.get_url()
    
    page_links = [x.a['href'] for x in page_list if x.a is not None]
    
    browser.open(base_url + next_on_suffix)
    
    next_on = browser.get_current_page()
    next_on_section = next_on.find('ol', attrs={'class':'highlight-box-wrapper'}) 
    
    next_up_dict = {}
    
    for item in next_on_section.find_all('li'):
        broadcast_info = item.find('div', attrs={'class':'programme__body programme__body--flush'})
        broadcast_info_tag = broadcast_info.find('div', attrs={'class': 'broadcast-event__time beta'})
        
        broadcast_date = broadcast_info_tag['title']
        broadcast_day = broadcast_info_tag.find('span', attrs={'class':'broadcast-event__date text-base timezone--date'}).get_text()
        broadcast_time = broadcast_info_tag.find('span',attrs = {'class': 'timezone--time'}).get_text()
        
        broadcast_channel = broadcast_info.find('div', attrs={'class': 'programme__service box-link__elevated micro text--subtle'})

        channel = broadcast_channel.a.get_text()
        channel_url = broadcast_channel.a['href']
        
        program_info = item.find('div', attrs={'class': 'grid 7/12 2/3@bpb2 3/4@bpw 5/6@bpw2 5/6@bpe'})
        program_title_info = program_info.a
        
        program_id = program_info.div['data-pid']
        program_link = program_title_info['href']
        program_title = program_title_info.find('span', attrs={'class': 'programme__title gamma'}).get_text()
        series = program_title_info.find('span', attrs={'class': 'programme__subtitle centi'}).get_text()
        program_synopsis = program_info.p.get_text()
        
        next_up_dict[program_id] = {'program_title': program_title.encode('utf-8'),
                                    'series': series.encode('utf-8'),
                                    'program_synopsis': program_synopsis.encode('utf-8').strip(),
                                    'program_link': program_link.encode('utf-8'),
                                    'channel': {'name': channel.encode('utf-8'),
                                              'link': channel_link.encode('utf-8')},
                                    'broadcast': {'date': broadcast_date.encode('utf-8'),
                                                 'day': broadcast_day.encode('utf-8'),
                                                 'time': broadcast_time.encode('utf-8')}}
        
    print(next_up_dict)
        
base_url = 'https://www.bbc.co.uk/programmes/b007y6k8/'
episodes_suffix = 'episodes/'
next_on_suffix = 'broadcasts/upcoming/'

browser.open(base_url + episodes_suffix)

episode_pagination_test()

