import base64
import subprocess

from eagleeye_ce import screenshot

def test_screenshot():
    data, url = screenshot.get_screenshot('google.com')
    assert len(data) > 1e5
    with open('test_screenshot.png', 'w') as f:
        f.write(base64.b64decode(data))
    #subprocess.check_call(['sensible-browser', 'test_screenshot.png'])
