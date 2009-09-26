from django.conf.urls.defaults import *
from django.contrib.comments.feeds import LatestCommentFeed
from django.contrib.syndication.views import feed
from blog.feeds import LatestPosts, PostCommentFeed
from blog.models import Post
from blog import views

info_dict = {
	'queryset': Post.objects.published(),
	'date_field': 'created_at',
}

urlpatterns = patterns('django.views.generic.date_based',

	(r'feeds/(?P<url>.*?)/$', feed, {'feed_dict': {
		'latest': LatestPosts,
		'comments': LatestCommentFeed,
		'articles': PostCommentFeed
	}}),
	
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
)