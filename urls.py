from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.sitemaps import FlatPageSitemap
from django.contrib.sitemaps.views import sitemap
from django.views.generic.simple import direct_to_template, redirect_to
from google.appengine.ext import ereporter
from ragendja.urlsauto import urlpatterns
from ragendja.auth.urls import urlpatterns as auth_patterns
from blog import sitemaps

admin.autodiscover()

handler500 = 'ragendja.views.server_error'

urlpatterns += auth_patterns + patterns('',
	
	# Blog
	(r'^blog/', include('blog.urls')),
	(r'^$', redirect_to, {'url': '/blog/', 'permanent': False}),

	(r'^admin/', include(admin.site.urls)),
	
	(r'^comments/', include('comments.urls')),
	
	(r'^pings/', include('trackback.urls')),
	
	(r'^auth/', include('auth.urls')),
	
	(r'^lifestream/', include('lifestream.urls')),

	#(r'^media/(?P<path>.*)$', 'django.views.static.serve',
	#	{'document_root': '/home/zanglang/djangoblog/media', 'show_indexes': True}),
		
	(r'^sitemap.xml$', sitemap, {'sitemaps': {
			'blog': sitemaps.BlogSitemap, 
			'flatpages': FlatPageSitemap }}),
		
	(r'^xd_receiver.htm$', direct_to_template, {'template': 'auth/xd_receiver.htm'}),
	
	(r'^_ah/xmpp/message/chat/$', 'blog.jabber.handler'),
	
	# Corrections
	(r'^articles/((?P<year>\d{4})/)?((?P<month>\d{2})/)?(?P<day>\d{1,2})*',
			'blog.views.redirect_to_blog'),
	(r'^(?P<year>\d{4})/((?P<month>\d{2})/)?(?P<day>\d{1,2})*',
			'blog.views.redirect_to_blog'),
	(r'^xml/*', redirect_to, {'url': 'http://feeds.feedburner.com/libcoffee', 'permanent': True}),
)
