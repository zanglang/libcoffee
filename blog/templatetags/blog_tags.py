from django import template
from comments.models import Comment
from blog.models import Category, Post
from google.appengine.api import memcache
from google.appengine.ext import db
import re

register = template.Library()


class LatestComments(template.Node):
	def __init__(self, limit, var_name):
		self.limit = limit
		self.var_name = var_name
 
	def render(self, context):
		comments = Comment.objects_public() \
			.order('-submit_date')[:int(self.limit)]
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
		context[self.var_name] = Category.all().order('title')
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
		context[self.varname] = db.get(self.object.categories)
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
		dates = memcache.get('blog-months')
		if dates is None:
			from datetime import datetime
			dates = []
			for p in Post.all().order('-created_at').fetch(1000):
				date = datetime(p.created_at.year, p.created_at.month, 1)
				if date not in dates:
					dates.append(date)
			memcache.add('blog-months', dates, 60*60*12)
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