#!/usr/bin/env python
from eagleeye_ce import tasks

try:
    query = raw_input('Shodan Query: ')
    tasks.get_shodan_results.delay(query)
except KeyboardInterrupt:
    exit()

