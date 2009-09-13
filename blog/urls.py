from django.conf.urls.defaults import *
from django.contrib.syndication.views import feed
from feeds import LatestPosts, ArticleFeed
from models import Post
import views

info_dict = {
	'queryset': Post.objects.filter(published=True),
	'date_field': 'created_at',
}

urlpatterns = patterns('django.views.generic.date_based',
	
	(r'(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
		'object_detail', dict(info_dict, slug_field='slug', month_format='%m'),
		'post_detail'),

	(r'(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{1,2})/$',
		'archive_day', dict(info_dict, month_format='%m')),

	(r'(?P<year>\d{4})/(?P<month>\d{2})/$',
		'archive_month', dict(info_dict, month_format='%m')),

	(r'(?P<year>\d{4})/$', 'archive_year', dict(info_dict)),

	(r'category/(?P<slug>[-\w]+)/$', views.category_detail),

	(r'categories/$', views.category_list),

	(r'^$', views.post_list),
	
	(r'feeds/(?P<url>.*?)/$', feed, {'feed_dict': {
		'latest': LatestPosts,
		'articles': ArticleFeed
	}}),
)