# django-openid-auth -  OpenID integration for django.contrib.auth
#
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

"""Glue between OpenID and django.contrib.auth."""

__metaclass__ = type

from django.conf import settings
from django.contrib.auth.models import User, Group
from openid.consumer.consumer import SUCCESS
from openid.extensions import sreg

from django_openid_auth import teams
from django_openid_auth.models import UserOpenID
from google.appengine.ext import db
from ragendja.dbutils import db_create
import logging

class IdentityAlreadyClaimed(Exception):
    pass


class OpenIDBackend:
    """A django.contrib.auth backend that authenticates the user based on
    an OpenID response."""

    def get_user(self, user_id):
        try:
            return db.get(user_id)
        except Exception:
            logging.debug(e)
            return None

    def authenticate(self, **kwargs):
        """Authenticate the user based on an OpenID response."""
        # Require that the OpenID response be passed in as a keyword
        # argument, to make sure we don't match the username/password
        # calling conventions of authenticate.

        openid_response = kwargs.get('openid_response')
        if openid_response is None:
            return None

        if openid_response.status != SUCCESS:
            return None

        user = None
        user_openid = UserOpenID.all().filter(
                'claimed_id =', openid_response.identity_url).get()
        if user_openid is None:
            if getattr(settings, 'OPENID_CREATE_USERS', False):
                user = self.create_user_from_openid(openid_response)
        else:
            user = user_openid.user

        if user is None:
            return None

        if getattr(settings, 'OPENID_UPDATE_DETAILS_FROM_SREG', False):
            sreg_response = sreg.SRegResponse.fromSuccessResponse(
                openid_response)
            if sreg_response:
                self.update_user_details_from_sreg(user, sreg_response)

        #teams_response = teams.TeamsResponse.fromSuccessResponse(
        #    openid_response)
        #if teams_response:
        #    self.update_groups_from_teams(user, teams_response)

        return user

    def create_user_from_openid(self, openid_response):
        sreg_response = sreg.SRegResponse.fromSuccessResponse(openid_response)
        if sreg_response:
            nickname = sreg_response.get('nickname', 'openiduser')
            email = sreg_response.get('email', '')
        else:
            nickname = 'openiduser'
            email = ''

        # Pick a username for the user based on their nickname,
        # checking for conflicts.
        i = 1
        while True:
            username = nickname
            if i > 1:
                username += str(i)
            try:
            	User.all().filter('username =', username)[0]
            except IndexError:
                break
            i += 1

        user = db_create(User, username, email, password=None)

        if sreg_response:
            self.update_user_details_from_sreg(user, sreg_response)

        self.associate_openid(user, openid_response)
        return user

    def associate_openid(self, user, openid_response):
        """Associate an OpenID with a user account."""
        # Check to see if this OpenID has already been claimed.
        try:
            user_openid = UserOpenID.all().filter(
                'claimed_id =', openid_response.identity_url)[0]
        except IndexError:
            user_openid = UserOpenID(
                user=user,
                claimed_id=openid_response.identity_url,
                display_id=openid_response.endpoint.getDisplayIdentifier())
            user_openid.save()
        else:
            if user_openid.user != user:
                raise IdentityAlreadyClaimed(
                    "The identity %s has already been claimed"
                    % openid_response.identity_url)

        return user_openid

    def update_user_details_from_sreg(self, user, sreg_response):
        fullname = sreg_response.get('fullname')
        if fullname:
            # Do our best here ...
            if ' ' in fullname:
                user.first_name, user.last_name = fullname.rsplit(None, 1)
            else:
                user.first_name = u''
                user.last_name = fullname

        email = sreg_response.get('email')
        if email:
            user.email = email
        user.save()

    def update_groups_from_teams(self, user, teams_response):
        teams_mapping = getattr(settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING', {})
        if len(teams_mapping) == 0:
            return
        if True: return

        current_groups = set(user.groups.filter(
                name__in=teams_mapping.values()))
        desired_groups = set(Group.all().filter(
                name__in=[teams_mapping[lp_team]
                          for lp_team in teams_response.is_member
                          if lp_team in teams_mapping]))
        for group in current_groups - desired_groups:
            user.groups.remove(group)
        for group in desired_groups - current_groups:
            user.groups.add(group)
