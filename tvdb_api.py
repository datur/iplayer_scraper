import json
import requests


class tvdb(object):
    ''' docstring for tvdb '''

    def __init__(self):
        ''' constructor '''
        self.apikey = None
        self._BASE_URL = "https://api.thetvdb.com"
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.search_type = {
            'name_search': '/search/series?name={0}',
            'series_search': '/series/{0}',
            'series_actors': '/series/{0}/actors',
            'series_episodes': '/series/{0}/episodes',
            'series_episodes_summary': '/series/{0}/episodes/summary',
            'episodes_information': '/episodes/{0}'
        }

    def login(self, key, userkey, username):
        '''gets login token for the tvdb api'''

        data = str.format(
            '{{"apikey": "{0}", "userkey": "{1}", "username": "{2}"}}', key,
            userkey, username)

        r = requests.post(
            'https://api.thetvdb.com/login', headers=self.headers, data=data)

        # convert to json in order to extract
        self.apikey = json.loads(r.text)['token']

        self.headers['Authorization'] = str('Bearer %s' % self.apikey)

    def search(self, search_term, search_type='name'):
        # TODO search type maybe?
        '''currently implimenting general search using a query string
        ie search_term='silent witness' will resurn the silent witness entry '''

        if search_type == 'name':
            url_modifier = self.search_type['name_search']
        if search_type == 'id':
            url_modifier = self.search_type['series_search']
        if search_type == 'episodes':
            url_modifier = self.search_type['series_episodes']
        if search_type == 'actors':
            url_modifier = self.search_type['series_actors']
        if search_type == 'episode_summary':
            url_modifier = self.search_type['series_episodes_summary']
        if search_type == 'specific_episode':
            url_modifier = self.search_type['episodes_information']

        url = self._BASE_URL + str.format(url_modifier,
                                          search_term.replace(' ', '%20'))
        r = requests.get(headers=self.headers, url=url)
        return r.json()

    def get_imdbID(self, search_term, show_match=False):
        ''' takes a search term as arguemtn and returns the imdb id for that item
            currently returns top search item result
        '''
        search_result = self.search(search_term)
        # TODO: use for each here to get list of show ids to match search term
        show_id = str(search_result['data'][0]['id'])
        search_result = self.search(show_id, search_type='id')

        # TODO: then search using this id to get imdb id

    def get_actors(self, search_term):
        ''' returns actors starring in the selected show '''
        search_result = self.search(search_term, 'episodes')
        print(search_result)


# testing

tvdb = tvdb()

tvdb.login(
    key="C3A1V1O3SWBRGA4H",
    userkey="SRLQ8PNDHOFKBN76",
    username="davidpaulturner35071m")

tvdb.search("silent witness")

tvdb.get_imdbID('silent witness')

tvdb.get_actors('76355')
