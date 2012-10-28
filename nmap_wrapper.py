# an (unimaginatively) named wrapper for nmap and the eagleeye
# http-detecting nse. Use to seed jobs into the task queue, using nmap
# to do the "is this worth screenshotting?" heavy lifting.

import subprocess
from eagleeye_ce import tasks

cmd = ['echo', '10.4.0.1:80\n10.4.0.2:80']

p = subprocess.Popen(cmd, bufsize=1, stdout=subprocess.PIPE)

while p.returncode is None:
    p.poll()
    line = p.stdout.readline().strip()
    if line:
        ip, port = line.rsplit(':', 1)
        tasks.get_screenshot.delay(ip, port)
