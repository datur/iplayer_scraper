# dictionay class for iplayer scraper v0.1
import json


class DictionaryBuilder(object):
    """docstring for DictionaryBuilder"""

    def __init__(self):
        super(DictionaryBuilder, self).__init__()

        self.parent_dict = {}

    def print(self):
        print(self.parent_dict)

    def clear(self):
        self.parent_dict = {}

    def update(self, key, value):
        try:
            self.parent_dict[key].update(value)
        except:
            print('key not valid')

    def add(self, value):
        self.parent_dict.update(value)

    def add(self, key, value):
        self.parent_dict.update({key: value})

    def to_json(self):
        return json.dumps(self.parent_dict)

    def to_file(self, file_name):
        with open(file_name, 'a') as f:
            json.dump(self.parent_dict, f)
            f.write('\n')
