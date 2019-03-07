from Extractor import Extractor
import argparse

# Iplayer Scraper v0.1

'''
ArgParse to handle:
	- file_name
	- full extract
	- show extract
	- genre extract
'''
ap = argparse.ArgumentParser(
    description="Iplayer scraper v0.2 Default usage: \n Python iplayer_scraper.py --all \n will save a-z of iplayer shows currently ~1360 shows into a json file.")
ap.add_argument('--all', help="returns a json file with all shows available", action='store_true')
ap.add_argument('--minimal', help="returns basic info for each show")
ap.add_argument('-v', '--verpose', help="whether to print debug information while running")

if __name__ == '__main__':
    args = ap.parse_args()
    if args.all is True:
        Extractor = Extractor()
        Extractor.extract()
    else:
        ap.print_help()
