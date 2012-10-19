sudo apt-get update
#sudo apt-get upgrade -y
sudo apt-get install unzip xvfb rabbitmq-server chromium-browser -y
curl http://python-distribute.org/distribute_setup.py | sudo python
curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | sudo python
sudo pip install celery selenium pyvirtualdisplay shodan librabbitmq
curl http://chromedriver.googlecode.com/files/chromedriver_linux64_23.0.1240.0.zip | funzip > chromedriver
chmod +x chromedriver
sudo mv chromedriver /usr/bin/chromedriver
