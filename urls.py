from django.conf.urls.defaults import patterns, url, include
from django.contrib.sitemaps import FlatPageSitemap
from django.contrib.sitemaps.views import sitemap
from django.views.generic.simple import direct_to_template, redirect_to
from blog import sitemaps

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
	url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	url(r'^admin/', include(admin.site.urls)),

	# Blog
	(r'^auth/', include('auth.urls')),
	(r'^blog/', include('blog.urls')),
	(r'^comments/', include('comments.urls')),
	(r'^lifestream/', include('lifestream.urls')),
	(r'^pings/', include('trackback.urls')),
	(r'^$', redirect_to, {'url': '/blog/', 'permanent': False}),
	(r'^xmlrpc/?$', 'django_xmlrpc.views.handle_xmlrpc'),
	(r'^xd_receiver.htm$', direct_to_template, {'template': 'auth/xd_receiver.htm'}),
	(r'^_ah/xmpp/message/chat/$', 'blog.jabber.handler'),
	('^_ah/warmup$', 'djangoappengine.views.warmup'),

	(r'^sitemap.xml$', sitemap, {'sitemaps': {
			'blog': sitemaps.BlogSitemap,
			'flatpages': FlatPageSitemap }}),

	# Corrections
	(r'^articles/((?P<year>\d{4})/)?((?P<month>\d{2})/)?(?P<day>\d{1,2})',
			'blog.views.redirect_to_blog'),
	(r'^(?P<year>\d{4})/((?P<month>\d{2})/)?(?P<day>\d{1,2})',
			'blog.views.redirect_to_blog'),
	(r'^category/', 'blog.views.redirect_to_blog'),
	(r'^xml/', redirect_to, {'url': 'http://feeds.feedburner.com/libcoffee', 'permanent': True}),
)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
