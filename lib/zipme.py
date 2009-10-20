#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
##########################################################################
ZipMe : GAE Content Downloader
##########################################################################
Just add this lines in your app.yaml :

- url: /zipme
  script: zipme.py

##########################################################################
"""                                                             # manatlan

from google.appengine.ext import webapp
from google.appengine.api import users

import wsgiref.handlers
import zipfile
import os,re,sys,stat
from cStringIO import StringIO

def createZip(path):

    def walktree (top = ".", depthfirst = True):
        names = os.listdir(top)
        if not depthfirst:
            yield top, names
        for name in names:
            try:
                st = os.lstat(os.path.join(top, name))
            except os.error:
                continue
            if stat.S_ISDIR(st.st_mode):
                for (newtop, children) in walktree (os.path.join(top, name),
                                                    depthfirst):
                    yield newtop, children
        if depthfirst:
            yield top, names

    list=[]
    for (basepath, children) in walktree(path,False):
          for child in children:
              f=os.path.join(basepath,child)
              if os.path.isfile(f):
                    f = f.encode(sys.getfilesystemencoding())
                    list.append( f )

    f=StringIO()
    file = zipfile.ZipFile(f, "w")
    for fname in list:
        nfname=os.path.join(os.path.basename(path),fname[len(path)+1:])
        file.write(fname, nfname , zipfile.ZIP_DEFLATED)
    file.close()

    f.seek(0)
    return f


class ZipMaker(webapp.RequestHandler):
    def get(self):
        if users.is_current_user_admin():
            #folder = os.path.dirname(__file__)
            folder = os.path.abspath('..') # assume we are in /lib
            self.response.headers['Content-Type'] = 'application/zip'
            self.response.headers['Content-Disposition'] = \
                    'attachment; filename="%s.zip"' % os.path.basename(folder)
            fid=createZip(folder)
            while True:
                buf=fid.read(2048)
                if buf=="": break
                self.response.out.write(buf)
            fid.close()
        else:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write("&lt;a href=\"%s\"&gt;You must be admin&lt;/a&gt;." %
                                    users.create_login_url("/zipme"))

def main():
    application = webapp.WSGIApplication(
                                       [('/zipme', ZipMaker)],
                                       debug=False)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()

