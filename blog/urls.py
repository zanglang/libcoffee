from django.conf.urls.defaults import *
from django.contrib.syndication.views import feed
from django.views.generic.create_update import create_object, update_object
from blog.feeds import LatestPosts, LatestComments, PostCommentFeed
from blog.models import Post
from blog.forms import PostForm
from blog import views, tasks

info_dict = {
	'queryset': Post.objects_published(),
	'date_field': 'created_at',
}

urlpatterns = patterns('',

	(r'feeds/(?P<url>.*?)/?$', feed, {'feed_dict': {
		'latest': LatestPosts,
		'comments': LatestComments,
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
	
	(r'preview/(?P<object_id>.+)/$', views.post_preview, {}, 'preview-post'),
	
	(r'fixtures/$', views.fixture_restore),
	(r'fixtures/dump/$', views.fixture_dump),
	
	#(r'tasks/send_trackback/$', tasks.send_trackback),
	(r'tasks/run_backup/$', tasks.run_backup),
	(r'tasks/maintenance/$', tasks.maintenance),

	(r'^$', views.post_list),
)