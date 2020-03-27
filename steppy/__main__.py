from argparse import ArgumentParser
from os.path import isfile
from .stepstone import StepStone


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

    if a.filter is None and a.output is None:
        s.results.print()
