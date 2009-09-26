from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.contrib.syndication.feeds import Feed, FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from blog.models import Post

current_site = Site.objects.get_current()

class LatestPosts(Feed):
	title = 'Libcoffee.net'
	link = '/blog'
	description = 'Libcoffee.net blog'
	ttl = '60'
	
	def items(self):
		return Post.objects.published().order_by('-updated_at')[:10]
	
	def item_author_name(self, item):
		return item.author.get_full_name()
	
	def item_categories(self, item):
		return item.categories.all()
	
	def item_pubdate(self, item):
		return item.created_at
	
class PostCommentFeed(Feed):
	title_template = 'feeds/comment.html'
	description_template = 'feeds/comment.html'
	
	def get_object(self, bits):
		if len(bits) != 4:
			raise ObjectDoesNotExist
		return Post.objects.get(created_at__year=bits[0], 
								created_at__month=bits[1], 
								created_at__day=bits[2],
								slug__iexact=bits[3])
	
	def title(self, obj):
		return 'Comments posted for %s - %s' % (obj.title, current_site.name)
	
	def link(self, obj):
		if not obj:
			raise FeedDoesNotExist
		return obj.get_absolute_url()
	
	def description(self, obj):
		return 'Comments posted on the entry %s' % obj.title
	
	def items(self, item):
		return Comment.objects.for_model(item).filter(is_public=True).order_by('-submit_date')
	
	def item_pubdate(self, item):
		return item.submit_date