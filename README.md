iBuff
=====
A small flask app for when you hit the gym

Just to be clear, this is less then a days work with loads of crappy code. I will probably work on it.

Installation 
------------

I assume you will be running a clean install of Ubuntu, if not then find your own way

Install supervisor and git

> apt-get install supervisor git
> service supervisor restart

Clone the repo

> cd /opt
> git clone https://github.com/jkaberg/iBuff.git

Install requirements (current Flask package in ubuntu repos is outdated)

> cd ibuff
> sudo pip install https://github.com/mitsuhiko/flask/tarball/master

Initialize the database

> flask --app=ibuff initdb

Edit main.py in app.config.update(), see SECRET_KEY, USERNAME and PASSWORD

> nano main.py

Create a supervisor config file

> nano /etc/supervisor/conf.d/ibuff.conf

Paste the following

> [program:ibuff]
> command=/opt/ibuff/main.py
> autostart=true
> autorestart=true
> stderr_logfile=/var/log/ibuff.err.log
> stdout_logfile=/var/log/ibuff.out.log

Tell supervisor to update and enact changes

> supervisorctl reread
> supervisorctl update

For more information on Supervisor: http://supervisord.org/

iBuff should now be running