# Taken from http://www.allyourpixel.com/post/metaweblog-38-django/
# and adapted for Libcoffee

from django.contrib.auth import authenticate
from django.contrib.sites.models import Site
from django_xmlrpc.decorators import xmlrpc_func, AuthenticationFailedException
from blog.models import Category, Post
from xmlrpclib import DateTime

# monkey patch -- http://bugs.cheetahtemplate.org/view.php?id=10
import inspect
inspect.imp.get_suffixes = lambda : [('.py', 'U', 1)]


def auth(username, password):
	user = authenticate(username=username, password=password)
	if user is None:
		raise AuthenticationFailedException
	return user


# example... this is what wordpress returns:
# {'permaLink': 'http://gabbas.wordpress.com/2006/05/09/hello-world/',
#  'description': 'Welcome to <a href="http://wordpress.com/">Wordpress.com</a>. This is your first post. Edit or delete it and start blogging!',
#  'title': 'Hello world!',
#  'mt_excerpt': '',
#  'userid': '217209',
#  'dateCreated': <DateTime u'20060509T16:24:39' at 2c7580>,
#  'link': 'http://gabbas.wordpress.com/2006/05/09/hello-world/',
#  'mt_text_more': '',
#  'mt_allow_comments': 1,
#  'postid': '1',
#  'categories': ['Uncategorized'],
#  'mt_allow_pings': 1}

def format_date(d):
	if not d: return None
	return DateTime(d.isoformat())

def post_struct(post):
	link = 'http://%s%s' % (Site.objects.get_current().domain, post.get_absolute_url())
	return {
		'postid': post.pk,
		'title': post.title,
		'link': link,
		'permaLink': link,
		'description': unicode(post.body),
		'categories': [c.pk for c in Category.get(post.categories)],
		'dateCreated': format_date(post.created_at),
		'userid': post.author.pk,
		# 'mt_excerpt': '',
		# 'mt_text_more': '',
		# 'mt_allow_comments': 1,
		# 'mt_allow_pings': 1}
	}

def category_struct(category):
	return {
		'categoryId': category.pk,
		'categoryName': unicode(category.title),
		'isPrimary': False
	}

def setTags(post, struct):
	tags = struct.get('categories', None)
	if tags is None:
		post.categories = []
	else:
		post.categories = [c.key() for c in Category.all().filter('title IN', tags)]


############## XML-RPC Methods ################

@xmlrpc_func(name='blogger.getUsersBlogs')
def blogger_getUsersBlogs(appkey, username, password):
	""" Blogger 1.0 API """
	auth(username, password)
	site = Site.objects.get_current()
	return [{
			'blogid': site.pk,
			'blogName': site.name,
			'url': 'http://%s' % site.domain }]

@xmlrpc_func(name='mt.getCategoryList')
def mt_getCategories(blogid, username, password):
	""" Movable Type API """
	auth(username, password)
	categories = Category.all()
	return [category_struct(c) for c in categories]

@xmlrpc_func(name='metaWeblog.getPost')
def metaWeblog_getPost(postid, username, password):
	""" MetaWeblog API """
	auth(username, password)
	post = Post.get(postid)
	return post_struct(post)

@xmlrpc_func(name='mt.getPostCategories')
def mt_getPostCategories(postid, username, password):
	""" Movable Type API """
	auth(username, password)
	post = Post.get(postid)
	categories = [category_struct(c) for c in Category.get(post.categories)]
	categories[0]['isPrimary'] = True # just pick one, it doesn't matter really.
	return categories

@xmlrpc_func(name='metaWeblog.getRecentPosts')
def metaWeblog_getRecentPosts(blogid, username, password, num_posts):
	""" MetaWeblog API """
	auth(username, password)
	posts = Post.all().order('-created_at').fetch(num_posts)
	return [post_struct(post) for post in posts]

@xmlrpc_func(name='metaWeblog.newPost')
def metaWeblog_newPost(blogid, username, password, struct, publish):
	""" MetaWeblog API """
	user = auth(username, password)
	post = Post(title=struct['title'],
				body=struct['description'],
				author=user,
				published=publish)
	setTags(post, struct)
	post.save()
	return post.pk

@xmlrpc_func(name='metaWeblog.editPost')
def metaWeblog_editPost(postid, username, password, struct, publish):
	""" MetaWeblog API """
	user = auth(username, password)
	post = Post.get(postid)
	if struct.has_key('title'):
		post.title = struct['title']
	if struct.has_key('description'):
		post.body = struct['description']
	post.author = user
	post.published = publish
	setTags(post, struct)
	post.save()
	return True

@xmlrpc_func(name='mt.setPostCategories')
def mt_setPostCategories(postid, username, password, categories):
	""" Movable Type API """
	auth(username, password)
	keys = [c['categoryId'] for c in categories]
	post = Post.get(postid)
	post.categories = Category.get(keys)
	post.save()
	return True

@xmlrpc_func(name='mt.publishPost')
def mt_publishPost(postid, username, password):
	""" Movable Type API """
	auth(username, password)
	post = Post.get(postid)
	post.published = True
	post.save()
	return True

@xmlrpc_func(name='blogger.deletePost')
def blogger_deletePost(appkey, postid, username, password, publish):
	""" Blogger 1.0 API """
	auth(username, password)
	post = Post.get(postid)
	post.delete()
	return True

@xmlrpc_func(name='metaWeblog.newMediaObject')
def metaWeblog_newMediaObject(blogid, username, password, struct):
	""" Not implemented """
	raise NotImplementedError
