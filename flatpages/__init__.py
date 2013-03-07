"""
models.py

App Engine datastore models

"""

import logging, re
from flask import Blueprint, current_app, render_template, Response, url_for
from google.appengine.api import taskqueue
from google.appengine.ext import db
from lxml import etree
from unicodedata import normalize
from cache import cache


app = Blueprint('flatpages', __name__, template_folder='.')

def slugify(text, delim=u'-'):
	"""Generates an slightly worse ASCII-only slug."""

	slug_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
	result = []
	for word in slug_re.split(text.lower()):
		word = normalize('NFKD', word).encode('ascii', 'ignore')
		if word:
			result.append(word)
	return unicode(delim.join(result))


class Flatpage(db.Model):
	""" Generic flat HTML page """

	url = db.StringProperty(required=True)
	title = db.StringProperty(required=True)
	content = db.TextProperty(required=True)

	def __unicode__(self):
		return u'%s' % self.title

	def _render(self):
		return render_template('flatpage.html', flatpage=self)

	def __html__(self):
		markedup = cache.get('markup_' + str(self.key()))
		if not markedup:
			# check markup library?
			func = current_app.jinja_env.filters.get('markup')
			if not func:
				return self.content

			markedup = func(self.content, 'Markdown')
			cache.set('markup_' + str(self.key()), markedup)

		return markedup

	@property
	def endpoint(self):
		return 'flatpages.' + slugify(self.url)

	def absolute_url(self, external=False):
		return url_for(self.endpoint, _external=external)


@app.route('/_gen_sitemap', methods=['GET', 'POST'])
def generate_sitemap():
	"""Deferred task to generate a Sitemap.xml for all published flat pages"""

	root = etree.Element('urlset', { 'attr': 'http://www.sitemaps.org/schemas/sitemap/0.9' })

	def add_url(location, last_modified=None, change_freq='always', priority=0.5):
		e = etree.SubElement(root, 'url')
		etree.SubElement(e, 'loc').text = location
		if last_modified:
			etree.SubElement(e, 'lastmod').text = last_modified.strftime('%Y-%m-%dT%H:%M:%S+00:00')
		etree.SubElement(e, 'changefreq').text = change_freq
		etree.SubElement(e, 'priority').text = str(priority)

	for p in Flatpage.all():
		add_url(p.absolute_url(external=True))

	logging.info('Generated sitemap.xml with %d flatpages.', len(root))
	xml = etree.tostring(root, encoding='utf-8', pretty_print=True, xml_declaration=True)
	cache.set('flatpages_sitemaps', xml)
	return xml


@cache.cached
@app.route('/sitemap.xml')
def sitemap():
	"""Returns a Sitemap.xml of all published flat pages"""

	xml = cache.get('flatpages_sitemaps')
	if not xml:
		logging.warning('Regenerating sitemaps.xml...')
		xml = generate_sitemap()

	return Response(xml, mimetype='text/xml')


# @app.route('/loaddata')
def load_json():
	"""Import existing data from JSON"""

	import json, os
	basepath = os.path.dirname(os.path.realpath(__file__))
	with open(os.path.join(basepath, 'flatpages.json')) as f:
		for entry in json.load(f):
			Flatpage(url=entry['url'],
					title=entry['title'],
					content=entry['content']).save()
	return "Done"


def register_flatpages(parentapp):
	"""Helper function to register URL routes for all Flatpages"""

	for page in Flatpage.all():
		parentapp.add_url_rule(page.url, page.endpoint, view_func=page._render)
		logging.debug('Registered: ' + page.url)
