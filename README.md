Simple Django and ElasticSearch Tutorial
========================================
<a href="http://www.opencrowd.com">![OpenCrowd][1]</a>
[1]: https://secure.gravatar.com/avatar/a6d183cba9fda35ebb550dbebd8b5d28?s=420&d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png

Requirements
------------

1.  An ElasticSearch instance
2.  Python & Django >= 1.4


Setup
-----

1. Clone this repo

>  git clone git://github.com/opencrowd/elasticsearch-tutorial.git


2. Create the ElasticSearch type mappings

> python manage.py put_mappings


3.  Run the server

> python manage.py runserver


4. Point your browser at http://localhost:8000/simple/



How It Works
------------

The project's views are defined in views.py.  The functions that query and store data into ElasticSearch are defined in models.py; these are purposefully kept minimal.

This project barely uses the Django ORM -- it uses it for the django.contrib.auth User model.  By default, it uses sqllite3 for this; you can (and should) configure it to point at an appropriate database configuration.

You can control the ElasticSearch index and connection via the ELASTICSEARCH_URL and ELASTICSEARCH_INDEX variables in settings.py.  These default to 'http://localhost:9200' and 'blog' respectively.

The only "fancy" thing that this tutorial app does beyond ElasticSearch CRUD-type operations is using akismet for spam detection for comments.  You should put your akismet key information in the apikey.txt file.  If you don't want to use akismet, you can disable that in settings.py defining USE_AKIMSET as False.

The web templates are kept purposefully simple, using bare minimum bootstrap functionality.

