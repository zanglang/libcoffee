from django.db import models
from google.appengine.ext import db
from django.db.models import permalink, signals
from django.contrib.auth.models import User
from trackback.signals import send_trackback
#from blog.managers import PostManager
import blog.ping
from ragendja.dbutils import cleanup_relations, KeyListProperty
import logging


class Category(db.Model):
	""" Blog Category """
	title = db.CategoryProperty(required=True)
	#slug = models.SlugField(unique=True)
	
	class Meta:
		verbose_name_plural = 'categories'
		ordering = ('title',)
	
	def __unicode__(self):
		return u'%s' % self.title
		
	@permalink
	def get_absolute_url(self):
		return ('blog.views.category_detail', (), {'slug': self.title})


class Post(db.Model):
	""" Blog Post """
	
	MarkupType = (
		# add more if needed
		'Markdown', # Markdown
		'reStructuredText', # restructuredText
		'Textile' #Textile
	)
	
	slug = db.StringProperty(multiline=False)
	title = db.StringProperty(multiline=False, required=True)
	author = db.ReferenceProperty(User)
	body = db.TextProperty(required=True)
	created_at = db.DateTimeProperty(auto_now_add=True)
	updated_at = db.DateTimeProperty(auto_now=True)
	published = db.BooleanProperty(default=False)
	#categories = models.ManyToManyField(Category, blank=True)
	categories = KeyListProperty(Category)
	#markuptype = models.CharField(max_length=1, choices=MarkupType, blank=True)
	markup = db.StringProperty(choices=MarkupType)
	#objects = PostManager()
	trackback_content_field_name = 'body'
	
	def __init__(self, *args, **kw):
		super(Post, self).__init__(*args, **kw)
		self._was_published = self.published
	
	def __unicode__(self):
		return u'%s' % self.title
		
	class Meta:
		ordering = ('-updated_at',)
		#get_latest_by = 'updated_at'
		
	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = title.replace(' ', '').lower()
		super(Post, self).save(*args, **kwargs)
		# newly published
		#if (not self._was_published and self.published):
		logging.debug('sending signals')
		send_trackback.send(sender=self.__class__, instance=self)
		
	@permalink
	def get_absolute_url(self):
		return ('blog.views.post_detail', (), {
			'slug': self.slug,
			'year': self.created_at.year,
			'month': self.created_at.strftime('%m').lower(),
			'day': self.created_at.day
		})
		
	@staticmethod
	def objects_published():
		return Post.all().filter('published =', True)
	
signals.pre_delete.connect(cleanup_relations, sender=Post)