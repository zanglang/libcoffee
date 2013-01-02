from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.db.models import permalink, signals
from datetime import datetime

class Category(models.Model):
	""" Blog Category """
	title = models.CharField(required=True)
	slug = models.CharField()

	class Meta:
		verbose_name_plural = 'categories'
		ordering = ('title',)

	def __unicode__(self):
		return u'%s' % self.title

	@permalink
	def get_absolute_url(self):
		return ('category-detail', self.slug or self.title)

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = self.title.lower()
		super(Category, self).save(*args, **kwargs)
		cache.clear()


class Post(models.Model):
	""" Blog Post """

	MarkupType = (
		# add more if needed
		'Markdown', # Markdown
		'reStructuredText', # restructuredText
		'Textile' #Textile
	)

	slug = models.CharField(multiline=False)
	title = models.CharField(multiline=False, required=True)
	author = models.ForeignKey(User)
	body = models.TextField(required=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	published = models.BooleanField(default=False)
	category = models.ForeignKey(Category)
	markup = models.CharField(choices=MarkupType)
	trackback_content_field_name = 'body'

	def __init__(self, *args, **kw):
		super(Post, self).__init__(*args, **kw)
		self._was_published = self.published

	def __unicode__(self):
		return u'%s' % self.title

	class Meta:
		ordering = ('-created_at',)

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = self.title.replace(' ', '').lower()
		if not self.created_at: # not sure why it's empty
			self.created_at = datetime.now()
		super(Post, self).save(*args, **kwargs)
		cache.clear()

	@permalink
	def get_absolute_url(self):
		return ('post-detail', (
				self.created_at.year,
				self.created_at.strftime('%m').lower(),
				self.created_at.day,
				self.slug))

	@staticmethod
	def objects_published():
		return Post.objects.filter('published =', True)
