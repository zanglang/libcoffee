from django.contrib.auth.models import User
from django.db import models
from django.db.models import permalink, signals
from datetime import datetime
import logging
from google.appengine.api import memcache
from google.appengine.ext import db
from ragendja.dbutils import cleanup_relations, KeyListProperty


class Category(db.Model):
	""" Blog Category """
	title = db.CategoryProperty(required=True)
	slug = db.StringProperty()
	
	class Meta:
		verbose_name_plural = 'categories'
		ordering = ('title',)
	
	def __unicode__(self):
		return u'%s' % self.title
		
	@permalink
	def get_absolute_url(self):
		return ('blog.views.category_detail', (), {'slug': self.slug or self.title})
	
	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = self.title.lower()
		super(Category, self).save(*args, **kwargs)
		memcache.flush_all()


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
	categories = KeyListProperty(Category)
	markup = db.StringProperty(choices=MarkupType)
	trackback_content_field_name = 'body'
	
	def __init__(self, *args, **kw):
		super(Post, self).__init__(*args, **kw)
		self._was_published = self.published
	
	def __unicode__(self):
		return u'%s' % self.title
		
	class Meta:
		ordering = ('-created_at',)
		#get_latest_by = 'updated_at'
		
	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = title.replace(' ', '').lower()
		if not self.created_at: # not sure why it's empty
			self.created_at = datetime.now()
		super(Post, self).save(*args, **kwargs)
		memcache.flush_all()
		
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
from blog.ping import *
from trackback.models import Trackback
signals.post_save.connect(send_trackback, sender=Post, dispatch_uid='send-trackback')
signals.post_save.connect(send_ping, sender=Post, dispatch_uid='send-ping')
signals.post_save.connect(trackback_check, sender=Trackback, dispatch_uid='trackback-filter')
