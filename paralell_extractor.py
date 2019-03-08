import multiprocessing
from joblib import Parallel, delayed
from Extractor import Extractor
from tqdm import tqdm
from datetime import datetime
from browser_class import Browser, JSBrowser


class ParallelExtractor(Extractor):

    def __init__(self):
        self.num_cores = multiprocessing.cpu_count()
        Extractor.__init__(self)
        self.filename = str('bbc_iplayer_scraped_' +
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '.json')

    def parallel_extract(self):

        initial_page = self.Browser.get_page(self._BASE_URL +
                                             self._SCRAPING_SUFFIX)

        atoz = initial_page.find('div', attrs={'class': "atoz-nav__inner"})
        navigation = atoz.find('ul', attrs={'class': 'scrollable-nav__track'})
        navigation_list = navigation.find_all('li')
        navigation_list = [
            x.a['href'] for x in navigation_list if x.a is not None
        ]

        Parallel(n_jobs=self.num_cores)(delayed(self.alphabet_char_extrator(suffix, self.filename))
                                        for suffix in tqdm(navigation_list))


if __name__ == '__main__':
    extract = ParallelExtractor()
    print(extract.num_cores)
    extract.parallel_extract()
