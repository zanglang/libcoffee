from django.conf.urls.defaults import patterns, url
from django.contrib.syndication.views import feed
from blog.feeds import LatestPosts, LatestComments, PostCommentFeed
from blog.views import * #@UnusedWildImport
from blog.tasks import * #@UnusedWildImport

urlpatterns = patterns('',

	(r'feeds/(?P<url>.*?)/?$', feed, {'feed_dict': {
		'latest': LatestPosts,
		'comments': LatestComments,
		'articles': PostCommentFeed
	}}),

	url(r'(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
		post_detail, name='post-detail'),

	url(r'(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{1,2})/$',
		post_archive_day, name='posts-by-day'),

	url(r'(?P<year>\d{4})/(?P<month>\d{2})/$',
		post_archive_month, name='posts-by-month'),

	url(r'(?P<year>\d{4})/$', post_archive_year, name='posts-by-year'),

	url(r'category/(?P<slug>[-\w]+)/$', category_detail, name='category-detail'),

	url(r'categories/$', category_list, name='category-list'),

	url(r'preview/(?P<object_id>.+)/$', post_preview, name='preview-post'),

	url(r'fixtures/$', fixture_restore),
	url(r'fixtures/dump/$', fixture_dump),

	url(r'tasks/run_backup/$', run_backup),
	url(r'tasks/maintenance/$', maintenance),

	url(r'^$', post_list, name='post-list'),
)
