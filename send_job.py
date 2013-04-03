#!/usr/bin/env python
from celery import group

from eagleeye_ce import nmap
from eagleeye_ce import screenshot
from eagleeye_ce import find


try:
    query = raw_input('Shodan Query: ')
    for x in range(1, 3):
        print "Querying page ", x
        c = (find.get_shodan_result.s(query, page=x) |
             nmap.filter_open.s())().get()
        group((screenshot.get_screenshot.s(host['ip'], host['port']) |
               screenshot.write_screenshot.s())
              for host in c).apply_async()

    #    tasks.get_shodan_result.apply_async(args=[query],
    #                                        queue='get_shodan_result')
    print "job sent"
except KeyboardInterrupt:
    pass
