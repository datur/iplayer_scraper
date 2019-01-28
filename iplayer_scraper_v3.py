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

# initail browser page
initial_page = Browser.get_page(BASE_URL + SCRAPING_SUFFIX)

navigation = initial_page.find('ul', attrs={'class': 'scrollable-nav__track'})
navigation_list = navigation.find_all('li')
navigation_list = [x.a['href'] for x in navigation_list if x.a is not None ]

programs_dictionary = {}

for suffix in navigation_list:
    web_page = Browser.get_page(BASE_URL + suffix)
    
    program_selection = web_page.find_all(
    'li', attrs={"class": "grid__item"})
    
    for program_box in program_selection: 
    	program_title, program_synopsis, latest_episode_url, episodes_available = Extractor.iplayer_atoz_page_extractor(program_box) 

    	program_website_url, program_credits_url, credits_available = Extractor.programme_website_extractor(Browser.get_page(latest_episode_url))

    	





		

