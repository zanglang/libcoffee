from django.conf.urls.defaults import *
from django.contrib.syndication.views import feed
from blog.feeds import LatestPosts, PostCommentFeed
from blog.models import Post
from blog import views
from comments.feeds import LatestCommentFeed

info_dict = {
	#'queryset': Post.objects.published(),
	'queryset': Post.all(),
	'date_field': 'created_at',
}

urlpatterns = patterns('',

	(r'feeds/(?P<url>.*?)/$', feed, {'feed_dict': {
		'latest': LatestPosts,
		'comments': LatestCommentFeed,
		'articles': PostCommentFeed
	}}),
	
	(r'(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
		views.post_detail),

	(r'(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{1,2})/$',
		#'archive_day', dict(info_dict, month_format='%m')),
		views.post_archive_day),

	(r'(?P<year>\d{4})/(?P<month>\d{2})/$',
		views.post_archive_month),

	(r'(?P<year>\d{4})/$', views.post_archive_year),

	(r'category/(?P<slug>[-\w]+)/$', views.category_detail),

	(r'categories/$', views.category_list),

	(r'^$', views.post_list),
)