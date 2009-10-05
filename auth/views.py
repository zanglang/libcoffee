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

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, \
	login as auth_login
from django.contrib.auth.models import User as DjangoUser
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django_openid_auth.forms import OpenIDLoginForm
from django_openid_auth.views import *
from openid.consumer.consumer import SUCCESS, CANCEL, FAILURE
from openid.consumer.discover import DiscoveryFailure
from openid.extensions import sreg
import logging
import urllib
from google.appengine.api import users as GoogleUsers
from auth.models import UserMapping



def google_login_begin(request):
	next = '%s?next=%s' % (reverse(google_login_complete), request.GET.get('next', ''))
	logging.debug('Google login - next is %s' % next)
	return HttpResponseRedirect(GoogleUsers.create_login_url(next))

def google_login_complete(request):
	try:
		user = GoogleUsers.get_current_user()
		logging.debug('Google login successful for %s' % user.email())
	except:
		 return render_failure(request, 'Google User details couldn\'t be found.')	
	# check if we have a local user that we may login as well
	try:
		mapping = UserMapping.all().filter('google_id =', user.user_id())[0]
		if request.user.is_anonymous():
			auth_login(request, mapping.user)
			logging.debug('mapped user to django user')
	except:
		logging.debug('Didn\'t find google user mapping')
		if request.user.is_authenticated():
			mapping = UserMapping(user=request.user, google_id=user.user_id())
			mapping.save()
	
	request.session['user_type'] = 'google'
	request.session['user_name'] = user.nickname()
	if '@' not in user.nickname(): # may not have full nick (eg dev server) 
		request.session['user_url'] = 'http://www.google.com/profiles/%s' % user.nickname() 
	request.session['user_email'] = user.email()
	logging.debug('login complete. redirecting to %s' % request.GET.get('next', ''))
	return HttpResponseRedirect(request.GET.get('next', ''))


def openid_login_begin(request, template_name='openid_login.html',
				redirect_field_name=REDIRECT_FIELD_NAME):
	"""Begin an OpenID login request, possibly asking for an identity URL."""
	redirect_to = request.REQUEST.get(redirect_field_name, reverse(openid_login_begin))

	# Get the OpenID URL to try.  First see if we've been configured
	# to use a fixed server URL.
	openid_url = getattr(settings, 'OPENID_SSO_SERVER_URL', None)

	if openid_url is None:
		if request.POST:
			login_form = OpenIDLoginForm(data=request.POST)
			if login_form.is_valid():
				openid_url = login_form.cleaned_data['openid_identifier']
		else:
			login_form = OpenIDLoginForm()

		# Invalid or no form data:
		if openid_url is None:
			return render_to_response(template_name, {
					'form': login_form,
					'request': request,
					redirect_field_name: redirect_to
				}, context_instance=RequestContext(request))

	error = None
	consumer = make_consumer(request)
	try:
		openid_request = consumer.begin(openid_url)
	except DiscoveryFailure, exc:
		return render_failure(
			request, "OpenID discovery error: %s" % (str(exc),), status=500)

	# Request some user details.
	openid_request.addExtension(
		sreg.SRegRequest(optional=['nickname', 'email', 'fullname']))

	# Construct the request completion URL, including the page we
	# should redirect to.
	return_to = request.build_absolute_uri(reverse(openid_login_complete))
	if redirect_to:
		if '?' in return_to:
			return_to += '&'
		else:
			return_to += '?'
		return_to += urllib.urlencode({redirect_field_name: redirect_to})

	return render_openid_request(request, openid_request, return_to)


def openid_login_complete(request, redirect_field_name=REDIRECT_FIELD_NAME):
	redirect_to = request.REQUEST.get(redirect_field_name, '')

	openid_response = parse_openid_response(request)
	if not openid_response:
		return render_failure(
			request, 'This is an OpenID relying party endpoint.')

	if openid_response.status == SUCCESS:
#===============================================================================
#		user = authenticate(openid_response=openid_response)
#		if user is not None:
#			if user.is_active:
#				auth_login(request, user)
#				return HttpResponseRedirect(sanitise_redirect_url(redirect_to))
#			else:
#				return render_failure(request, 'Disabled account')
#		else:
#			return render_failure(request, 'Unknown user')
#===============================================================================
		sreg_response = sreg.SRegResponse.fromSuccessResponse(openid_response)
		if sreg_response:
			username = sreg_response.get('fullname', '')
			if username == '':
				username = sreg_response.get('nickname', 'Some user')
			request.session['user_type'] = 'openid'
			request.session['user_name'] = username
			request.session['user_url'] = openid_response.identity_url
			request.session['user_email'] = sreg_response.get('email', '')			
		else:
			return render_failure(request,
					'This OpenID provider does not support Simple Registration')
		
			
		return HttpResponseRedirect(sanitise_redirect_url(redirect_to))
	
	elif openid_response.status == FAILURE:
		return render_failure(request, 'OpenID authentication failed: %s' %
			openid_response.message)
	elif openid_response.status == CANCEL:
		return render_failure(request, 'Authentication cancelled')
	else:
		assert False, (
			"Unknown OpenID response type: %r" % openid_response.status)