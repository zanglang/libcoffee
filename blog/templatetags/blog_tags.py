from django import template
from django.core.cache import cache as memcache
from blog.models import Category, Post
from comments.models import Comment
from keycache import serialize_models, deserialize_models

from datetime import datetime
import re

register = template.Library()


class LatestComments(template.Node):
	def __init__(self, limit, var_name):
		self.limit = limit
		self.var_name = var_name

	def render(self, context):
		comments = deserialize_models(memcache.get('blog-latest-comments'))
		if comments is None:
			comments = Comment.objects_public() \
					.order('-submit_date')[:int(self.limit)]
			memcache.add('blog-latest-comments', serialize_models(comments))
		if comments and (int(self.limit) == 1):
			context[self.var_name] = comments[0]
		else:
			context[self.var_name] = comments
		return ''

@register.tag
def get_latest_comments(parser, token):
	try:
		tag_name, arg = token.contents.split(None, 1)
	except ValueError:
		raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
	m = re.search(r'(.*?) as (\w+)', arg)
	if not m:
		raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
	format_string, var_name = m.groups()
	return LatestComments(format_string, var_name)


class BlogCategories(template.Node):
	def __init__(self, var_name):
		self.var_name = var_name

	def render(self, context):
		categories = deserialize_models(memcache.get('blog-categories'))
		if categories is None:
			categories = Category.all().order('title')
			memcache.add('blog-categories', serialize_models(categories))
		context[self.var_name] = categories
		return ''


@register.tag
def get_blog_categories(parser, token):
	try:
		tag_name, arg = token.contents.split(None, 1)
	except ValueError:
		raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
	m = re.search(r'as (\w+)', arg)
	if not m:
		raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
	var_name = m.groups()[0]
	return BlogCategories(var_name)


class CategoriesFor(template.Node):
	def __init__(self, obj, varname):
		self.varname = varname
		self.obj_name = obj

	def render(self, context):
		self.object = template.resolve_variable(self.obj_name, context)
		categories = deserialize_models(memcache.get('categories-for-' + self.object.pk))
		if not categories:
			categories = Category.get(self.object.categories)
			memcache.set('categories-for-' + self.object.pk, serialize_models(categories))
		context[self.varname] = categories
		return ''

@register.tag
def get_categories_for(parser, token):
	bits = token.contents.split()
	if len(bits) != 4:
		raise template.TemplateSyntaxError, "get_categories_for tag takes exactly three arguments"
	if bits[2] != 'as':
		raise template.TemplateSyntaxError, "second argument to get_categories_for tag must be 'as'"
	return CategoriesFor(bits[1], bits[3])


class MonthList(template.Node):
	def __init__(self, var_name):
		self.var_name = var_name

	def render(self, context):
		posts = Post.objects_published().order('-created_at')
		dates = memcache.get('months-list')
		if dates is None:
			dates = []
			for p in posts:
				date = datetime(p.created_at.year, p.created_at.month, 1)
				if not date in dates:
					dates.append(date)
			memcache.set('months-list', dates)
		context[self.var_name] = dates
		return ''

@register.tag
def get_month_list(parser, token):
	try:
		tag_name, arg = token.contents.split(None, 1)
	except ValueError:
		raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
	m = re.search(r'as (\w+)', arg)
	if not m:
		raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
	var_name = m.groups()[0]
	return MonthList(var_name)
