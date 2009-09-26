from django.conf.urls.defaults import *
from django.contrib import admin
from blog import sitemaps
from auth import views as auth_views
from django_openid_auth.views import logo as openid_logo

admin.autodiscover()

urlpatterns = patterns('',
	
	# Blog
	(r'^blog/', include('blog.urls')),
	(r'^$', 'django.views.generic.simple.redirect_to',
		{'url': '/blog/', 'permanent': False}),

	(r'^admin/', include(admin.site.urls)),
	
	(r'^comments/', include('django.contrib.comments.urls')),
	
	(r'^pings/', include('trackback.urls')),

	(r'^media/(?P<path>.*)$', 'django.views.static.serve',
		{'document_root': '/home/zanglang/djangoblog/media', 'show_indexes': True}),
		
	(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap',
		{'sitemaps': { 'blog': sitemaps.BlogSitemap }}),
		
	(r'^auth/', include('auth.urls')),
)
