#!/usr/bin/env python
from eagleeye_ce import tasks

query = raw_input('Shodan Query: ')
tasks.get_shodan_results.delay(query)
