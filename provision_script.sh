sudo apt-get update
#sudo apt-get upgrade -y
sudo apt-get install git unzip xvfb rabbitmq-server nmap chromium-browser -y
#sudo apt-get install build-essential python-dev -y # optional for librabbitmq
curl http://python-distribute.org/distribute_setup.py | sudo python
curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | sudo python

#sudo pip install librabbitmq # optional for queue performance
curl http://chromedriver.googlecode.com/files/chromedriver_linux64_23.0.1240.0.zip | funzip > chromedriver
chmod +x chromedriver
sudo mv chromedriver /usr/bin/chromedriver
git clone git@github.com:PaulMcMillan/eagleeye_ce.git
cd eagleeye_cd
sudo pip install -U -r requirements.txt
