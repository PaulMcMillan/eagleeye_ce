import subprocess

from lxml import objectify

from eagleeye_ce import celery
from eagleeye_ce import utils


@celery.task
def verify_open(hosts, ports):
    """ Basic quick nmap open port command. Returns a list of open
    service,host,port tuples.
    """
    hosts, ports = utils.iterit(hosts, ports, cast=str)

    command = ['nmap', '-T5', '--no-stylesheet', '--open', '-Pn', '-sT',
               '--min-rate', '500', '--host-timeout', '5s',
               '-oX', '-',  # output XML to stdout
               '-p', ','.join(ports)] + hosts
    nmap_xml_output = subprocess.check_output(command)
    nmaprun = objectify.fromstring(nmap_xml_output)

    result = []
    for host in nmaprun.host[:]:
        for port in host.ports.port:
            item = (port.service.get('name'),
                    host.address.get('addr'),
                    port.get('portid'))
            result.append(item)
    print result
    return result

