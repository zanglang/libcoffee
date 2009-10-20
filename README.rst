.. -*- coding: utf-8 -*-

Libcoffee.net Blog Engine
=========================
:Author: Jerry Chong
:Contact: zanglang@gmail.com
:Website: http://www.libcoffee.net/
:Version: 0.1 (perpetually alpha ;)
:Copyright: Creative Commons Attribution-Share Alike



1. Introduction
---------------
This is the codebase used for the blog application at http://www.libcoffee.net/.
Libcoffee.net is written based on the `Django <http://www.djangoproject.com>`_
framework, and is intended to be run on a
`Google App Engine <http://code.google.com/appengine/>`_ account.


2. Installation
---------------
Libcoffee.net depends on a bunch of Python libraries and some custom Django apps
that were ported to App Engine's BigTable. Check out the Dependencies section
for details. Fill out ``settings.py`` for app configuration, or use
``local_settings.py`` if you prefer.

After that, it's the same as starting up Django's development server::

  echo 'Just running the dev server'
  ./manage.py runserver
  echo 'and uploading to AppEngine...'
  common/.google_appengine/appcfg.py update .


3. Dependencies
---------------
- `app-engine-patch <http://code.google.com/p/app-engine-patch/>`_
- Django 1.1 (bundled with app-engine-patch)
- Google App Engine SDK (latest, follow aep's setup instructions)
- `pygments <http://pygments.org/>`_
- `python-dateutil <http://labix.org/python-dateutil>`_
- `python-openid <http://openidenabled.com/python-openid/>`_
- `python-simplejson <http://www.undefined.org/python/>`_
- `python-docutils <http://docutils.sourceforge.net/>`_ (optional)
- `django-openid-auth <http://github.com/zanglang/django-openid-auth-appengine>`_
  (AppEngine port)

Some libraries are already checked in to Git...

- `BeautifulSoup <http://www.crummy.com/software/BeautifulSoup/>`_
- PyFacebook
- `python-feedparser <http://www.feedparser.org/>`_
- `python-markdown <http://www.freewisdom.org/projects/python-markdown/>`_
- `python-textile <http://loopcore.com/python-textile/>`_

Also included are a few Django apps ported to App Engine, and heavily modified:

- django.contrib.comments
- `django-trackback <http://code.google.com/p/django-trackback/>`_

All libraries are expected to be in the ``lib/`` folder, or in a ZIP archive and
placed in ``common/zip-packages``.


4. License
----------
Libcoffee.net is licensed under the `Creative Commons Attribution-Share Alike
<http://creativecommons.org/licenses/by-sa/3.0/>`_ license.

All third-party parts shamelessly included here are distributed under their
respective licenses.


