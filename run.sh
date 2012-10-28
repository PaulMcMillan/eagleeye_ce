# This is an example script for running eagleeye_ce on a single
# machine. You may want your own copy of this script to customize it.

# Clear out any leftover tasks from previous runs
celery purge

# Get a query from the command line and insert it into the queue
./send_job.py

# Run workers that consume all of the task queues
celery -A eagleeye_ce.tasks worker --loglevel=info -Q get_shodan_results,get_screenshot,write_screenshot

# Alternatively, we could split it out so that you can consume the
# screenshots from one machine while gathering them on other
# machines. Be sure you have customized settings.py to point to the
# correct rabbitmq server.

# On the cloud server
#celery -A eagleeye_ce.tasks worker --loglevel=info -Q get_shodan_results,get_screenshot

# On the image destination
#celery -A eagleeye_ce.tasks worker --loglevel=info -Q write_screenshot
