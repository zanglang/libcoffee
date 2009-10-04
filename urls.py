from django.conf.urls.defaults import *
from django.contrib import admin
from ragendja.urlsauto import urlpatterns
from ragendja.auth.urls import urlpatterns as auth_patterns
from blog import sitemaps

admin.autodiscover()

handler500 = 'ragendja.views.server_error'

urlpatterns += auth_patterns + patterns('',
	
	# Blog
	(r'^blog/', include('blog.urls')),
	(r'^$', 'django.views.generic.simple.redirect_to',
		{'url': '/blog/', 'permanent': False}),

	(r'^admin/', include(admin.site.urls)),
	
	(r'^comments/', include('comments.urls')),
	
	(r'^pings/', include('trackback.urls')),

	#(r'^media/(?P<path>.*)$', 'django.views.static.serve',
	#	{'document_root': '/home/zanglang/djangoblog/media', 'show_indexes': True}),
		
	(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap',
		{'sitemaps': { 'blog': sitemaps.BlogSitemap }}),
		
	(r'^auth/', include('auth.urls')),
)
