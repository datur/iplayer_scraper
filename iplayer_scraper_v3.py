# main.py

import json
import hashlib
from bs4 import BeautifulSoup
import sys
from extractor_class import Extractor
from browser_class import Browser
'''
ArgParse to handle:
	- file_name
	- full extract
	- show extract
	- genre extract
'''

if __name__ == '__main__':
    X = Extractor()
    X.extract()
