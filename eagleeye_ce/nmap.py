import subprocess

from lxml import objectify

from eagleeye_ce import celery
from eagleeye_ce import utils


@celery.task
def filter_open(hosts):
    """ Basic quick nmap open port command. Filters a list of
    shodan-style hosts/port results to those that are open.

    This is inefficient, but n ~= 100 so it doesn't matter much.
    """
    host_list = list(set(h['ip'] for h in hosts))
    port_list = set(str(h['port']) for h in hosts)

    command = ['nmap', '-T5', '--no-stylesheet', '-Pn', '-sT',
               '--min-rate', '500', '--host-timeout', '15s',
               '-oX', '-',  # output XML to stdout
               '-p', ','.join(port_list)] + host_list
    nmap_xml_output = subprocess.check_output(command)
    nmaprun = objectify.fromstring(nmap_xml_output)

    checked = {}
    for host in nmaprun.host:
        for port in host.ports.port:
            state = port.state.get('state')
            checked[host.address.get('addr'), port.get('portid')] = state

    result = []
    for host in hosts:
        if checked[host['ip'], str(host['port'])] == 'open':
            result.append(host)
    return result

