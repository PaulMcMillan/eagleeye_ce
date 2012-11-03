#!/usr/bin/env python
from eagleeye_ce import tasks

try:
    query = raw_input('Shodan Query: ')
    tasks.get_shodan_result.apply_async(args=[query],
                                        queue='get_shodan_result')
except KeyboardInterrupt:
    pass
