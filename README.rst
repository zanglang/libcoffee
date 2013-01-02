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
Libcoffee.net is now written using the `Flask <http://flask.pocoo.org>`_
microframework, and is intended to be run on a
`Google App Engine <http://code.google.com/appengine/>`_ account.


2. Features
-----------
Basic features:

- Basic blog publishing with plain URLs eg 'blog/2009/12/31/slug'
- Content markup with reStructuredText, Markdown and Textile
- Clean default template with Bootstrap CSS, hAtom microformats
- Code block syntax highlighting

Several features have been dropped or 'unimplemented' in favor of using
third-party services, or due to deprecation:

- Post creation and editing (via Google App Engine administration)
- Comments, email notifications and spam checking (via Disqus)
- Email notifications of new comments (via Disqus)
- Scheduled datastore backup via Blobstore (via Google App Engine cron jobs)

Work-in-progress:

- Movable Type/MetaWeblog API


3. Installation
---------------
Libcoffee.net depends on the AppEngine Python SDK, the excellent
`flask-appengine-template <http://github.com/kamalgill/flask-appengine-template>`_,
as well as a few Python libraries.

If you've cloned this repository from Github, `flask-appengine-template` should
already have been linked as a git submodule. To populate the folder::

  git submodule update --init flask-appengine-template

Symlink or copy out everything under `flask-appengine-template/src` to the main
folder. Python modules under `4. Dependencies`_ can be symlinked/copied to the
'lib' folder, the app will pick them up automatically.

After that, it's the same as starting up AppEngine's development server::

  echo 'Just running the dev server'
  google_appengine/dev_appserver.py .
  echo 'and uploading to AppEngine...'
  google_appengine/appcfg.py update .


4. Dependencies
---------------
- `flask-appengine-template <http://github.com/kamalgill/flask-appengine-template>`_
- Google App Engine SDK (latest)

Install with Python package manager of choice:

- `BeautifulSoup.py <http://www.crummy.com/software/BeautifulSoup/>`_
- `docutils <http://docutils.sourceforge.net/>`_
   - `roman.py` also needs to be copied separately into the `lib` folder.
- `markdown <http://packages.python.org/Markdown/>`_
- `pygments <http://pygments.org/>`_
- `textile <https://github.com/jsamsa/python-textile>`_


5. Changelog
------------
- 0.2: Major rewrite, now based on Flask/Werkzeug
- 0.1: Initial release with Django


6. License
----------
Libcoffee.net is licensed under the `Creative Commons Attribution-Share Alike
<http://creativecommons.org/licenses/by-sa/3.0/>`_ license.

All third-party parts shamelessly included here are distributed under their
respective licenses.
