# django-openid-auth -  OpenID integration for django.contrib.auth
#
# Copyright (C) 2007 Simon Willison
# Copyright (C) 2008-2009 Canonical Ltd.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import base64
import time

from openid.association import Association as OIDAssociation
from openid.store.interface import OpenIDStore
from openid.store.nonce import SKEW

from django_openid_auth.models import Association, Nonce
from google.appengine.ext import db


class DjangoOpenIDStore(OpenIDStore):
    def __init__(self):
        self.max_nonce_age = 6 * 60 * 60 # Six hours

    def storeAssociation(self, server_url, association):
        assoc = Association(
            server_url=server_url,
            handle=association.handle,
            secret=base64.encodestring(association.secret),
            issued=association.issued,
            lifetime=association.lifetime,
            assoc_type=association.assoc_type)
        assoc.save()

    def getAssociation(self, server_url, handle=None):
        assocs = []
        if handle is not None:
            assocs = Association.all() \
            	.filter('server_url =', server_url) \
            	.filter('handle =', handle).fetch(1000)
        else:
            assocs = Association.all().filter('server_url =', server_url).fetch(1000)
        associations = []
        expired = []
        for assoc in assocs:
            association = OIDAssociation(
                assoc.handle, base64.decodestring(assoc.secret), assoc.issued,
                assoc.lifetime, assoc.assoc_type
            )
            if association.getExpiresIn() == 0:
                expired.append(assoc)
            else:
                associations.append((association.issued, association))
        for assoc in expired:
            assoc.delete()
        if not associations:
            return None
        associations.sort()
        return associations[-1][1]

    def removeAssociation(self, server_url, handle):
        assocs = Association.all() \
            	.filter('server_url =', server_url) \
            	.filter('handle =', handle).fetch(1000)
        assocs_exist = len(assocs) > 0
        db.delete(assocs)
        return assocs_exist

    def useNonce(self, server_url, timestamp, salt):
        if abs(timestamp - time.time()) > SKEW:
            return False
           
        try:
            ononce = Nonce.all() \
            	.filter('server_url =', server_url) \
                .filter('timestamp =', timestamp) \
                .filter('salt =', salt)[0]
        except:
            ononce = Nonce(
                server_url=server_url,
                timestamp=timestamp,
                salt=salt)
            ononce.save()
            return True

        return False

    def cleanupNonces(self, _now=None):
        if _now is None:
            _now = int(time.time())
        expired = Nonce.all().filter('timestamp <', _now - SKEW).fetch(1000)
        count = len(expired)
        if count:
            db.delete(expired)
        return count

    def cleanupAssociations(self):
        now = int(time.time())
        #expired = Association.objects.extra(
        #    where=['issued + lifetime < %d' % now])
        raise Exception # not done
        count = expired.count()
        if count:
            expired.delete()
        return count
