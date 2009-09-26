from django.conf.urls.defaults import *
from django.contrib.auth.views import logout
from django_openid_auth.views import logo as openid_logo
from auth import views

urlpatterns = patterns('',
	(r'logout$', logout),
	(r'openid_login/$', views.openid_login_begin),
	(r'openid_login/complete$', views.openid_login_complete),
	url(r'openid_logo$', openid_logo, name = 'openid-logo'),
)