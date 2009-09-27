from django.db import models
from django.db.models import permalink
from django.contrib.auth.models import User
from django.contrib.syndication.feeds import Feed
from django.contrib.sitemaps import Sitemap
from trackback.signals import send_trackback
from blog.managers import PostManager
import blog.ping


class Category(models.Model):
	""" Blog Category """
	title = models.CharField(max_length=100)
	slug = models.SlugField(unique=True)
	
	class Meta:
		verbose_name_plural = 'categories'
		ordering = ('title',)
	
	def __unicode__(self):
		return u'%s' % self.title
		
	@permalink
	def get_absolute_url(self):
		return ('blog.views.category_detail', (), {'slug': self.slug})


class Post(models.Model):
	""" Blog Post """
	
	MarkupType = (
		# add more if needed
		('r', 'RestructuredText'),
	)
	
	slug = models.SlugField(unique_for_date='created_at')
	title = models.CharField(max_length=140)
	author = models.ForeignKey(User)
	body = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	published = models.BooleanField()
	categories = models.ManyToManyField(Category, blank=True)
	markuptype = models.CharField(max_length=1, choices=MarkupType, blank=True)
	objects = PostManager()
	trackback_content_field_name = 'body'
	
	def __init__(self, *args, **kw):
		super(Post, self).__init__(*args, **kw)
		self._was_published = self.published
	
	def __unicode__(self):
		return u'%s' % self.title
		
	class Meta:
		ordering = ('-updated_at',)
		get_latest_by = 'updated_at'
		
	class Admin:
		list_display = ('title', 'created_at', 'published')
		list_filter = ('created_at', 'categories', 'published')
		search_fields = ('title', 'body')
		
	def save(self, *args, **kwargs):
		super(Post, self).save(*args, **kwargs)
		# newly published
		if (not self._was_published and self.published):
			print 'sending signals'
			send_trackback.send(sender=self.__class__, instance=self)
		
	@permalink
	def get_absolute_url(self):
		return ('post_detail', (), {
			'slug': self.slug,
			'year': self.created_at.year,
			'month': self.created_at.strftime('%m').lower(),
			'day': self.created_at.day
		})
		
