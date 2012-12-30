"""
models.py

App Engine datastore models

"""

from datetime import datetime
from google.appengine.ext import db


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
	author = db.UserProperty()
	body = db.TextProperty(required=True)
	created_at = db.DateTimeProperty(auto_now_add=True)
	updated_at = db.DateTimeProperty(auto_now=True)
	published = db.BooleanProperty(default=False)
	category = db.CategoryProperty()
	markup = db.StringProperty(choices=MarkupType)

	def __init__(self, *args, **kw):
		super(Post, self).__init__(*args, **kw)
		self._was_published = self.published

	def __unicode__(self):
		return u'%s' % self.title

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = self.title.replace(' ', '').lower()
		if not self.created_at: # not sure why it's empty
			self.created_at = datetime.now()
		super(Post, self).save(*args, **kwargs)

	@staticmethod
	def objects_published():
		return Post.all().filter('published =', True)
