#from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.contrib.syndication.feeds import Feed, FeedDoesNotExist
from django.core.cache import cache as memcache
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from datetime import datetime
from dateutil.relativedelta import relativedelta
from blog.models import Post, Category
from comments.models import Comment
from comments.feeds import LatestCommentFeed
from keycache import serialize_models, deserialize_models


class CustomFeed(Rss201rev2Feed):
	"""Custom feed generator that implements generic feed extensions"""
	
	def add_root_elements(self, handler):
		super(CustomFeed, self).add_root_elements(handler)
		handler.addQuickElement('generator', 'Libcoffee.net/Django')
		handler.addQuickElement('webMaster', 'admin@libcoffee.net')
		handler.addQuickElement('geo:lat', '3.106789',
				{'xmlns:geo': 'http://www.w3.org/2003/01/geo/wgs84_pos#'})
		handler.addQuickElement('geo:long', '101.592145',
				{'xmlns:geo': 'http://www.w3.org/2003/01/geo/wgs84_pos#'})


class CustomPostFeed(CustomFeed):
	""" Custom feed generator that implements custom feedback-based RSS extensions.
	Used for the blog Post model only."""
	
	def add_item_elements(self, handler, item):
		super(CustomPostFeed, self).add_item_elements(handler, item)
		handler.addQuickElement('trackback:ping',
				'http://%s%s' % (Site.objects.get_current().domain,
				reverse('receive_trackback', kwargs={'object_id': item['key']})),
				{'xmlns:trackback': 'http://madskills.com/public/xml/rss/module/trackback/'})
		handler.addQuickElement('wfw:commentRss',
				item['link'].replace('blog', 'blog/feeds/articles'),
				{'xmlns:wfw': 'http://wellformedweb.org/CommentAPI/'})


class LatestPosts(Feed):
	"""RSS Feed for latest posts on the blog"""
	title = 'Libcoffee.net'
	description = 'Just another Django weblog'
	copyright = 'Copyleft (c) 2009, Jerry Chong'
	link = '/blog/'
	ttl = '60'
	feed_type = CustomPostFeed
	description_template = 'feeds/post.html'
	
	def description(self, obj):
		return 'Lastest posts from %s' % Site.objects.get_current().name
	
	def items(self):
		posts = deserialize_models(memcache.get('feed-latest-posts'))
		if not posts:
			posts = Post.objects_published().order('-created_at').fetch(30)
			memcache.set('feed-latest-posts', serialize_models(posts))
		return posts
	
	def item_author_name(self, item):
		return item.author.get_full_name()
	
	def item_categories(self, item):
		categories = deserialize_models(memcache.get('categories-for-' + item.pk))
		if not categories:
			categories = Category.get(item.categories)
			memcache.set('categories-for-' + item.pk, serialize_models(categories))
		return categories
	
	def item_pubdate(self, item):
		return item.created_at
	
	def item_extra_kwargs(self, item):
		return { 'key': item.pk } 


class LatestComments(LatestCommentFeed):
	"""RSS Feed for latest comments on the blog.
	Overrides the default implementation by the comments app."""
	
	feed_type = CustomFeed
	title_template = 'feeds/comment_title.html'
	description_template = 'feeds/comment.html'	
	
	def item_link(self, item):
		return item.get_absolute_url()


class PostCommentFeed(Feed):
	"""RSS Feed for all comments posted to a blog post"""
	
	feed_type = CustomFeed
	title_template = 'feeds/comment_title.html'
	description_template = 'feeds/comment.html'
	
	def get_object(self, bits):
		if len(bits) != 4:
			raise ObjectDoesNotExist
		date = datetime(int(bits[0]), int(bits[1]), int(bits[2]))
		post = deserialize_models(memcache.get('post-for-' + str(date)))
		if not post:
			post = Post.objects_published() \
					.filter('slug =', bits[3]) \
					.filter('created_at >=', date) \
					.filter('created_at <', date + relativedelta(days=+1)).get()
			memcache.set('post-for-' + str(date), serialize_models(post))
		return post
	
	def title(self, obj):
		return 'Comments posted for %s - %s' % (obj.title, Site.objects.get_current().name)
	
	def link(self, obj):
		if not obj:
			raise FeedDoesNotExist
		return obj.get_absolute_url()
	
	def description(self, obj):
		return 'Comments posted on the entry %s' % obj.title
	
	def items(self, item):
		comments = deserialize_models(memcache.get('comments-for-' + item.pk))
		if not comments:
			comments = Comment.objects_public() \
					.filter('content_object =', item) \
					.order('-submit_date').fetch(1000)
			memcache.set('comments-for-' + item.pk, serialize_models(comments))
		return comments 
	
	def item_pubdate(self, item):
		return item.submit_date
