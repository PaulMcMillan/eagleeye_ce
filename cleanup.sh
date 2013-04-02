# Simple script to kill anything which might be left hanging around
# during a crash or debugging
celery purge
sudo rabbitmqctl stop_app
sudo rabbitmqctl reset
sudo rabbitmqctl start_app
sudo pkill celery
sudo pkill Xvfb
sudo pkill chromedriver
ps axf
rm -f chromedriver.log
rm -f *.pyc
rm -f *~
rm -f out/*
