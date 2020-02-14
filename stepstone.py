#!/usr/bin/python3
from requests import get
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from progressbar import ProgressBar
from os.path import isfile
from json import dump


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
        ret = req.find_all("main", attrs={"class": "offer__content"})[1].text
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
        print("saved results to '{0}'.".format(path))

    def filter(self, text):
        ret = []
        for res in self.results:
            if text.lower() in res.offer_content.lower():
                ret.append(res)
        return ret


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
        print("fetching results for '{0}' {1} km around {2}.".format(keyword, km, plz))
        r = get(url)
        soup = BeautifulSoup(r.content, parser="lxml", features="lxml")   # fetches first page
        self.get_result_count(soup)
        i = 0
        with ProgressBar(0, self.result_count) as pb:
            while (i * self.INDEX_STEP) < self.result_count:
                pb.update(len(self.results.results))
                self.get_results(soup)
                i += 1
                soup = BeautifulSoup(get(self.format_base_url(keyword, plz, km, i + 1)).content, parser="lxml",
                                     features="lxml")
        print("found %i/%i job offers" % (len(self.results.results), self.result_count))
        return self.results


def generate_valid_outfile(path):
    if not path.endswith(".json"):
        path += ".json"
    if isfile(path):
        print("file '{0}' already exists.".format(path))
        generate_valid_outfile(path.split(".")[0] + "1")
    return path


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument("-s", "--search", help="job title or skill", type=str)
    ap.add_argument("-p", "--postal", help="your postal code", type=str)
    ap.add_argument("-r", "--range", help="range in km", type=str)
    ap.add_argument("-f", "--filter", nargs='+', help="filters for a keyword in the offer text", type=str)
    ap.add_argument("-o", "--output", help="save results to json file", type=str)
    a = ap.parse_args()
    if a.search is None:
        print("no search query specified. exiting")
        exit()
    if a.range is None:
        a.range = ""
    if a.postal is None:
        a.postal = ""

    s = StepStone()
    try:
        s.fetch(a.search, a.postal, a.range)
    except KeyboardInterrupt:
        print("\ncaught ctrl+c")

    if a.output is not None:
        print("saving results to file")
        s.results.save(generate_valid_outfile(a.output))

    if a.filter is not None:
        print("filtering results")
        for f in a.filter:
            results = s.results.filter(a.filter)
            if len(results) > 0:
                print(results)
            else:
                print("no matches for '{0}' found.".format(f))
