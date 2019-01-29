# main.py

import json
import hashlib
from bs4 import BeautifulSoup
import sys
from extractor_class import Extractor
from browser_class import Browser

# variable instantiation

BASE_URL = 'https://www.bbc.co.uk'
SCRAPING_SUFFIX = '/iplayer/a-z/'

Browser = Browser()
Extractor = Extractor()

# initail browser page
initial_page = Browser.get_page(BASE_URL + SCRAPING_SUFFIX)

navigation = initial_page.find('ul', attrs={'class': 'scrollable-nav__track'})
navigation_list = navigation.find_all('li')
navigation_list = [x.a['href'] for x in navigation_list if x.a is not None]

programs_dict = {}

for suffix in navigation_list:
    web_page = Browser.get_page(BASE_URL + suffix)

    program_selection = web_page.find_all('li', attrs={"class": "grid__item"})

    for program_box in program_selection:
        program_title, program_synopsis, latest_episode_url, episodes_available = Extractor.iplayer_atoz_page_extractor(
            program_selection=program_box)

        program_website_url, program_credits_url, credits_available = Extractor.programme_website_extractor(
            Browser.get_page(BASE_URL + latest_episode_url))

        if program_website_url or program_credits_url:
            credits, genre_format = Extractor.latest_episode_page(
                Browser.get_page(BASE_URL + program_credits_url
                                 if credits_available else BASE_URL +
                                 program_website_url), credits_available)

        _id = latest_episode_url.split('/')
        _id = _id[-2]
        programs_dict[_id] = {
            'program title':
            program_title,
            'program_synopsis':
            program_synopsis,
            'episodes_available':
            episodes_available,
            'program_website':
            BASE_URL + program_website_url
            if program_website_url is not None else None,
            'credits_available':
            credits_available,
            'latest_episode': {
                'latest_episode_url':
                BASE_URL + latest_episode_url
                if latest_episode_url is not None else None,
                'credits':
                credits
            }
        }
        if genre_format is not None:
            programs_dict[_id].update(genre_format)
    print(programs_dict)
