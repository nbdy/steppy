## steppy
[![Build Status](https://build.eberlein.io/buildStatus/icon?job=python_steppy)](https://build.eberlein.io/job/python_steppy/)
### why?
i can not be bothered to read through all the job offers.
### how to use it?
#### cli
```
└──╼ $./stepstone.py -h
usage: stepstone.py [-h] [-s SEARCH] [-p POSTAL] [-r RANGE]
                    [-f FILTER [FILTER ...]] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -s SEARCH, --search SEARCH
                        job title or skill
  -p POSTAL, --postal POSTAL
                        your postal code
  -r RANGE, --range RANGE
                        range in km
  -f FILTER [FILTER ...], --filter FILTER [FILTER ...]
                        filters for a keyword in the offer text
  -o OUTPUT, --output OUTPUT
                        save results to json file

ex: ./stepstone.py -s android -p 45127 -r 50 -o out.json -f "home office"
```
#### code
```python
from steppy.stepstone import StepStone
ss = StepStone()
results = ss.fetch("android", "45127", 50)
results.save("output.json")
filtered_results = results.filter("home office")
```
