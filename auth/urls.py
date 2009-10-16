from django.conf.urls.defaults import *
from django.contrib.auth.views import logout
from django_openid_auth.views import logo as openid_logo
from auth import views

urlpatterns = patterns('',
	(r'logout$', logout),
	
	# OpenID
	(r'openid_login/$', views.openid_login_begin),
	(r'openid_login/complete$', views.openid_login_complete),
	url(r'openid_logo$', openid_logo, name = 'openid-logo'),
	
	# Google
	(r'google_login/$', views.google_login_begin),
	(r'google_login/complete$', views.google_login_complete),
	
	# Facebook
	(r'facebook_login/$', views.facebook_login_complete),
)