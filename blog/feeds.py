#from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.contrib.syndication.feeds import Feed, FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from dateutil.relativedelta import relativedelta
from google.appengine.ext import db
from blog.models import Post
from comments.models import Comment


class LatestPosts(Feed):
	title = 'Libcoffee.net'
	link = '/blog'
	description = 'Libcoffee.net blog'
	ttl = '60'
	
	def items(self):
		return Post.objects_published().order('-updated_at').fetch(10)
	
	def item_author_name(self, item):
		return item.author.get_full_name()
	
	def item_categories(self, item):
		return db.get(item.categories)
	
	def item_pubdate(self, item):
		return item.created_at
	
class PostCommentFeed(Feed):
	title_template = 'feeds/comment.html'
	description_template = 'feeds/comment.html'
	
	def get_object(self, bits):
		if len(bits) != 4:
			raise ObjectDoesNotExist
		date = datetime(int(bits[0]), int(bits[1]), int(bits[2]))
		return Post.objects_published() \
				.filter('slug =', bits[3]) \
				.filter('created_at >=', date) \
				.filter('created_at <', date + relativedelta(days=+1)).get()
	
	def title(self, obj):
		return 'Comments posted for %s - %s' % (obj.title, Site.objects.get_current().name)
	
	def link(self, obj):
		if not obj:
			raise FeedDoesNotExist
		return obj.get_absolute_url()
	
	def description(self, obj):
		return 'Comments posted on the entry %s' % obj.title
	
	def items(self, item):
		return Comment.objects_public().filter('content_object =', item) \
				.order('-submit_date').fetch(1000)
	
	def item_pubdate(self, item):
		return item.submit_date