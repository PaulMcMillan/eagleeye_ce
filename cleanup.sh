sudo pkill celery
sudo pkill Xvfb
sudo pkill chromedriver
ps axf
rm -f chromedriver.log
rm -f *.pyc
rm -f *~
rm -f out/*