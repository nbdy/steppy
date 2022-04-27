from argparse import ArgumentParser
from os.path import isfile
from steppy.Stepstone import StepStone
from loguru import logger as log


def generate_valid_outfile(path):
    if not path.endswith(".json"):
        path += ".json"
    if isfile(path):
        print("file '{0}' already exists.".format(path))
        generate_valid_outfile(path.split(".")[0] + "1")
    return path


def main():
    ap = ArgumentParser()
    ap.add_argument("-s", "--search", help="job title or skill", type=str)
    ap.add_argument("-p", "--postal", help="your postal code", type=str)
    ap.add_argument("-r", "--range", help="range in km", type=str)
    ap.add_argument("-f", "--filter", nargs='+', help="filters for a keyword in the offer text", type=str)
    ap.add_argument("-o", "--output", help="save results to json file", type=str)
    a = ap.parse_args()
    if a.search is None:
        log.error("No search query specified!")
        exit()
    if a.range is None:
        a.range = ""
    if a.postal is None:
        a.postal = ""

    s = StepStone()
    try:
        s.fetch(a.search, a.postal, a.range)
    except KeyboardInterrupt:
        log.info("\nCaught CTRL+C")

    if a.output is not None:
        fn = generate_valid_outfile(a.output)
        log.info("Saving results to file '{}'.", fn)
        s.results.save(fn)

    if a.filter is not None:
        log.info("Filtering results...")
        for f in a.filter:
            results = s.results.filter(a.filter)
            if len(results) > 0:
                print(results)
            else:
                log.info("No matches found for '{}'.", f)

    if a.filter is None and a.output is None:
        s.results.print()


if __name__ == '__main__':
    main()
