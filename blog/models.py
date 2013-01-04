"""
models.py

"""

import re
from datetime import datetime
from decorators import permalink
from google.appengine.api import memcache
from google.appengine.ext import db
from unicodedata import normalize

from blog.markup import markup


def slugify(text, delim=u'-'):
	"""
	Generates an slightly worse ASCII-only slug.
	
	http://flask.pocoo.org/snippets/5/
	"""

	slug_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
	result = []
	for word in slug_re.split(text.lower()):
		word = normalize('NFKD', word).encode('ascii', 'ignore')
		if word:
			result.append(word)
	return unicode(delim.join(result))


class Category(db.Model):
	"""Blog Category"""

	title = db.CategoryProperty(required=True)

	def __init__(self, *args, **kw):
		super(Category, self).__init__(*args, **kw)
		if not self.title[:1].isupper():
			self.title = self.title.capitalize()

	def __html__(self):
		return u'%s' % self.title

	def save(self, *args, **kwargs):
		memcache.delete('categories-all-cached')
		super(Category, self).save(*args, **kwargs)

	@permalink
	def absolute_url(self, external=False):
		return 'blog.posts_by_category', {
			'category': self.title,
			'_external': external
		}

	@staticmethod
	def all_cached():
		c = memcache.get('categories-all-cached')
		if not c:
			c = sorted(c.title for c in Category.all())
			memcache.set('categories-all-cached', c)
		return c


class Post(db.Model):
	"""Blog Post"""

	MarkupType = (
		# add more if needed
		'Markdown',  # Markdown
		'reStructuredText',  # restructuredText
		'Textile'  # Textile
	)

	slug = db.StringProperty(multiline=False)
	title = db.StringProperty(multiline=False, required=True)
	author = db.UserProperty()
	body = db.TextProperty(required=True)
	created_at = db.DateTimeProperty(auto_now_add=True)
	updated_at = db.DateTimeProperty(auto_now=True)
	published = db.BooleanProperty(default=False)
	categories = db.StringListProperty(default=[])
	markup = db.StringProperty(choices=MarkupType)

	def __init__(self, *args, **kw):
		super(Post, self).__init__(*args, **kw)
		self._was_published = self.published

	def __html__(self):
		markedup = memcache.get('markup_' + str(self.key()))
		if not markedup:
			markedup = markup(self.body, self.markup)
			memcache.set('markup_' + str(self.key()), markedup)

		return markedup

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.title)
		if not self.created_at:  # not sure why it's empty
			self.created_at = datetime.now()

		# add missing categories
		for c in self.categories:
			if not c in Category.all_cached():
				Category(title=c).save()

		# reset cached keys
		memcache.flush_all()
		super(Post, self).save(*args, **kwargs)

	@permalink
	def absolute_url(self, external=False):
		return 'blog.post_detail', {
			'slug': self.slug,
			'year': self.created_at.year,
			'month': self.created_at.strftime('%m').lower(),
			'day': self.created_at.day,
			'_external': external
		}

	@staticmethod
	def objects_published():
		return Post.all().filter('published =', True)
