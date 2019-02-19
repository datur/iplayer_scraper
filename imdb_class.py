from imdb import IMDb


class IMDB(object):
    ''' docstring for IMDB '''

    def __init__(self):
        ''' constructor '''
        self.im = IMDb()

    def find(self, name):
        ''' search imdb for movie or show '''
        s_result = self.im.search_movie(name)
        return s_result

    def get(self, imdb_id):
        return self.im.get_movie(imdb_id)

    def search(self, keyword):
        return self.im.search_keyword(keyword)

    def update_episodes(self, imdb_obj):
        self.im.update(series, 'episodes')

    def get_id(self, show_object):
        pass
