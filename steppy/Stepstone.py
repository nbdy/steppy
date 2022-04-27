from requests import get
from bs4 import BeautifulSoup
from progressbar import ProgressBar
from json import dump
from loguru import logger as log


class Result(object):
    title = None
    posted = None
    city = None
    short_text = None
    listing_url = None
    offer_content = None

    def __init__(self, result_soup):
        self.title = result_soup.find("h2").text
        self.posted = result_soup.find("time").text
        self.city = result_soup.find("li", attrs={"class": "job-element__body__location"}).text
        tmp = result_soup.find("a", attrs={"data-offer-meta-text-snippet-link": "true"})
        self.requirements = tmp.text
        self.listing_url = "https://stepstone.de" + tmp["href"]
        self.offer_content = self.fetch_offer_content()

    def fetch_offer_content(self):
        req = BeautifulSoup(get(self.listing_url).content, parser="lxml", features="lxml")
        ret = req.find_all("main", attrs={"class": "offer__content"})
        if len(ret) < 1:
            ret = req.find_all("js-app-ld-ContentBlock")
        return ret


class Results(object):
    results = []

    def add(self, result):
        self.results.append(result)

    def _prepare_data(self):
        r = []
        for res in self.results:
            r.append(res.__dict__)
        return r

    def save(self, path):
        data = self._prepare_data()
        with open(path, "w") as fp:
            dump(data, fp)

    def filter(self, text):
        ret = []
        for res in self.results:
            if text.lower() in res.offer_content.lower():
                ret.append(res)
        return ret

    def print(self, keys=None):
        if keys is None:
            keys = ["title", "requirements", "posted", "city", "listing_url"]
        for r in self.results:
            d = r.__dict__
            for k in keys:
                print("{0}:\t{1}".format(k, d[k]))
            print()


class StepStone(object):
    debug = False

    INDEX_STEP = 25
    BASE_URL = "https://www.stepstone.de/5/job-search-simple.html?stf=freeText&ns=1&qs=%5B%5D&companyID=0&cityID=0&" \
               "sourceOfTheSearchField=resultlistpage%3Ageneral&searchOrigin=Resultlist_top-search&ke={0}&ws={1}&" \
               "ra={2}&of={3}&action=paging_next"

    result_count = 0
    results = Results()

    def __init__(self, debug=False):
        self.debug = debug

    def format_base_url(self, keyword, plz, km, page=1):
        if page > 1:
            page = page * self.INDEX_STEP  # there are 25 shown items per page
        return self.BASE_URL.format(keyword, plz, km, str(page))

    def get_result_count(self, soup):
        self.result_count = int(soup.find("span", attrs={"class": "at-facet-header-total-results"}).text)

    def get_results(self, soup):
        c = soup.find("div", attrs={"data-resultlist-offers-total": str(self.result_count)}).find_all("article")
        i = 0
        with ProgressBar(i, len(c)) as pb:
            while i < len(c):
                pb.update(i)
                self.results.add(Result(c[i]))
                i += 1

    def fetch(self, keyword, plz, km):
        url = self.format_base_url(keyword, plz, km)
        if self.debug:
            print(url)

        log.debug("Fetching results for '{}' {} km around {}.", keyword, km, plz)
        soup = BeautifulSoup(get(url).content, parser="lxml", features="lxml")   # fetches first page
        self.get_result_count(soup)
        i = 0
        with ProgressBar(0, self.result_count) as pb:
            while (i * self.INDEX_STEP) < self.result_count:
                pb.update(len(self.results.results))
                self.get_results(soup)
                i += 1
                soup = BeautifulSoup(get(self.format_base_url(keyword, plz, km, i + 1)).content, parser="lxml",
                                     features="lxml")
        log.debug("Found {}/{} offers.", len(self.results.results), self.result_count)
        return self.results
