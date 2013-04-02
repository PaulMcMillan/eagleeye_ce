import socket
import pytest

from pprint import pprint

from eagleeye_ce import find
from eagleeye_ce import nmap
from eagleeye_ce import screenshot


@pytest.fixture
def host_list():
    res = find.get_shodan_result('org:amazon')
#    pprint(res)
    return res


def test_basic_nmap():
    hosts = [{'ip': socket.gethostbyname('google.com'),
             'port': 80,},
             {'ip': '10.21.33.84',
              'port': 9833}]
    res = nmap.filter_open(hosts)
    print res


def test_nmap(host_list):
     res = nmap.verify_open(host_list)
     assert type(res) is list
     # It's reasonable for at least some to be up and down
     assert len(host_list) != len(res)

# def test_selenium():
#     screenshot.get_screenshot('google.com')
