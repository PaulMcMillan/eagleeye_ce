from eagleeye_ce import celery
from celery import chain
from eagleeye_ce import nmap
from eagleeye_ce import screenshot

import socket
from time import sleep


hosts = [{'ip': socket.gethostbyname('google.com'),
          'port': 80,},]

#def test_basic_chain():
#    c = chain(nmap.filter_open.s(hosts), nmap.filter_open.s())()

def test_screenshot_chain():
    c = chain(screenshot.get_screenshot.s('google.com'),
              screenshot.write_screenshot.s())()
