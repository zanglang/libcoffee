.. -*- coding: utf-8 -*-

Libcoffee.net Blog Engine
=========================
:Author: Jerry Chong
:Contact: zanglang@gmail.com
:Website: http://www.libcoffee.net/
:Version: 0.2 (perpetually alpha ;)
:Copyright: Creative Commons Attribution-Share Alike



1. Introduction
---------------
This is the codebase used for the blog application at http://www.libcoffee.net/.
Libcoffee.net is now written based on the `Flask <http://flask.pocoo.org>`_
framework, and is intended to be run on a
`Google App Engine <http://code.google.com/appengine/>`_ account. Version 0.1
was previously based on `Django <http://www.djangoproject.com/>`_, but has since
been rewritten.


2. Features
-----------
Basic features:

- Basic blog publishing with plain URLs eg 'blog/2009/12/31/slug'
- Content markup with reStructuredText, Markdown and Textile
- Clean default template with Bootstrap CSS, hAtom microformats
- Code block syntax highlighting

Several features have been dropped in favor of using third-party services, or
due to deprecation:

- Post creation and editing (Google App Engine administration)
- Comments, email notifications and spam checking (Disqus)
- Email notifications of new comments (Disqus)

Work-in-progress:

- Scheduled datastore backup via email
- Movable Type/MetaWeblog API


3. Installation
---------------
Libcoffee.net depends on the AppEngine Python SDK, the excellent
`flask-appengine-template <http://github.com/kamalgill/flask-appengine-template>`_
to run, as well as a few Python libraries.

If you've cloned this repository from Github, `flask-appengine-template` should
already have been checked out as a git submodule. Symlink or copy out those
subdirectories under `flask-appengine-template/src` to the main folder. Python
modules under `4. Dependencies`_ can be symlinked/copied to a subfolder 'lib',
the Flask app will pick them up automatically.

After that, it's the same as starting up AppEngine's development server::

  echo 'Just running the dev server'
  google_appengine/dev_appserver.py .
  echo 'and uploading to AppEngine...'
  google_appengine/appcfg.py update .


4. Dependencies
---------------
- `flask-appengine-template <http://github.com/kamalgill/flask-appengine-template>`_
- Google App Engine SDK (latest)

Install with pip or package manager of choice:

- `BeautifulSoup.py <http://www.crummy.com/software/BeautifulSoup/>`_
- `pygments <http://pygments.org/>`_
- `python-docutils <http://docutils.sourceforge.net/>`_

   - `roman.py` also needs to be copied separately into the `lib` folder.

- `python-markdown <http://packages.python.org/Markdown/>`_
- `python-textile <https://github.com/jsamsa/python-textile>`_


5. License
----------
Libcoffee.net is licensed under the `Creative Commons Attribution-Share Alike
<http://creativecommons.org/licenses/by-sa/3.0/>`_ license.

All third-party parts shamelessly included here are distributed under their
respective licenses.

