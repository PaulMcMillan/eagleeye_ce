sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install unzip xvfb rabbitmq-server redis-server chromium-browser -y
sudo pip install celery selenium pyvirtualdisplay redis
curl http://chromedriver.googlecode.com/files/chromedriver_linux64_23.0.1240.0.zip | funzip > chromedriver
chmod +x chromedriver
sudo mv chromedriver /usr/bin/chromedriver
