"""
views.py
"""

import logging
from datetime import datetime, timedelta
from flask import abort, render_template, request, Response, url_for
from google.appengine.api import memcache, users
from google.appengine.ext import db, deferred
from lxml import etree
from werkzeug.contrib.atom import AtomFeed

from blog import app
from blog.models import Category, Post
from blog.paginator import Paginator

POSTS_PER_PAGE = 5


def get_posts(year, month=None, day=None, slug=None):
	"""Helper function to load posts, optionally by year, month, day and slug"""

	queryset = Post.objects_published().order('-created_at')
	date = datetime(int(year), month and int(month) or 1, day and int(day) or 1)
	if date > datetime.now():
		abort(404)
	date2 = timedelta(days=(month is None and 365 or day is None and 31 or 1))
	if slug:
		queryset = queryset.filter('slug =', slug)
	return queryset.filter('created_at >=', date) \
				.filter('created_at <', date + date2)


def render_posts_paginated(query):
	"""Helper function to wrap a list of Posts with a Paginator"""

	page = request.args.get('page')
	if page and page.isdigit():
		page = int(page)
		if page < 1:
			abort(404)
	else:
		page = 1

	posts = query.run(offset=(page - 1) * POSTS_PER_PAGE, limit=POSTS_PER_PAGE)
	if not posts and page != 1:
		abort(404)

	return render_template('post_list.html', posts=posts,
			paginator=Paginator(page, POSTS_PER_PAGE, query.count()))


@app.route('/')
def index():
	"""Main page"""

	q = Post.objects_published().order('-created_at')
	return render_posts_paginated(q)


@app.route('/<int:year>/', defaults={ 'month': None, 'day': None })
@app.route('/<int:year>/<int:month>/', defaults={ 'day': None })
@app.route('/<int:year>/<int:month>/<int:day>/')
def posts_by_date(year, month, day):
	"""Page listing posts for a date range"""

	q = get_posts(year, month, day)
	return render_posts_paginated(q)


@app.route('/category/<category>/')
def posts_by_category(category):
	"""Page listing posts for a category"""

	q = Post.objects_published().order('-created_at') \
			.filter('categories =', category)
	return render_posts_paginated(q)


@app.route('/<int:year>/<int:month>/<int:day>/<slug>/')
def post_detail(year, month, day, slug):
	"""Page displaying one blog post"""

	p = get_posts(year, month, day, slug).get() or abort(404)
	return render_template('post_detail.html', post=p)


@app.route('/_gen_months', methods=['GET', 'POST'])
def generate_post_months():
	"""Deferred task to generate a list of months for all blog posts"""

	months = set()
	for p in db.Query(Post, projection=('created_at',)):
		months.add(datetime(p.created_at.year, p.created_at.month, 1))
	memcache.set('list-post-months', sorted(months))
	return 'OK'


@app.route('/_gen_sitemap', methods=['GET', 'POST'])
def generate_sitemap():
	"""Deferred task to generate a Sitemap.xml for all published blog posts"""

	root = etree.Element('urlset', { 'attr': 'http://www.sitemaps.org/schemas/sitemap/0.9' })

	def add_url(location, last_modified=None, change_freq='always', priority=0.5):
		e = etree.SubElement(root, 'url')
		etree.SubElement(e, 'loc').text = location
		if last_modified:
			etree.SubElement(e, 'lastmod').text = last_modified.strftime('%Y-%m-%dT%H:%M:%S+00:00')
		etree.SubElement(e, 'changefreq').text = change_freq
		etree.SubElement(e, 'priority').text = str(priority)

	for p in Post.objects_published().order('-created_at'):
		add_url(p.absolute_url(external=True), p.updated_at)

	for c in Category.all():
		add_url(c.absolute_url(external=True))

	add_url(url_for('blog.index', _external=True), priority=1.0)
	add_url(url_for('blog.latest_posts', _external=True))

	logging.info('Generated sitemap.xml with %d blog posts', len(root))
	xml = etree.tostring(root, encoding='utf-8', pretty_print=True, xml_declaration=True)
	memcache.set('blog_sitemaps', xml)
	return xml


@app.route('/sitemap.xml')
def sitemap():
	"""Returns a Sitemap.xml of all publised blog posts"""

	xml = memcache.get('blog_sitemaps')
	if not xml:
		logging.warning('Regenerating sitemaps.xml...')
		xml = generate_sitemap()

	return Response(xml, mimetype='text/xml')


@app.route('/feeds/latest/')
def latest_posts():
	feed = AtomFeed('Libcoffee.net', feed_url=request.url, url=request.url_root)
	for p in Post.objects_published().order('-created_at')[:POSTS_PER_PAGE]:
		feed.add(p.title, unicode(p.__html__()),
				content_type='html',
				author=p.author.nickname(),
				url=p.absolute_url(external=True),
				updated=p.updated_at,
				published=p.created_at)
	return Response(feed.to_string(), mimetype='application/atom+xml')


##### Miscellaneous

@app.app_context_processor
def list_categories():
	return { 'categories': Category.all_cached() }

@app.app_context_processor
def list_post_months():
	months = memcache.get('list-post-months') or []
	if not months:
		logging.warning('Regenerating list of months by post...')
		deferred.defer(generate_post_months)
	return { 'months': months }

@app.app_template_filter('timesince')
def timesince(dt, past_="ago",
	future_="from now",
	default="just now"):
	"""
	Returns string representing "time since"
	or "time until" e.g.
	3 days ago, 5 hours from now etc.
	"""

	now = datetime.utcnow()
	if now > dt:
		diff = now - dt
		dt_is_past = True
	else:
		diff = dt - now
		dt_is_past = False

	periods = (
		(diff.days / 365, "year", "years"),
		(diff.days / 30, "month", "months"),
		(diff.days / 7, "week", "weeks"),
		(diff.days, "day", "days"),
		(diff.seconds / 3600, "hour", "hours"),
		(diff.seconds / 60, "minute", "minutes"),
		(diff.seconds, "second", "seconds"),
	)

	for period, singular, plural in periods:
		if period:
			return "%d %s %s" % (period, \
				singular if period == 1 else plural, \
				past_ if dt_is_past else future_)

	return default

@app.app_template_filter('naturalday')
def naturalday(date, datefmt):
	delta = date.date() - datetime.now().date()
	if delta.days == 0:
		return 'today'
	elif delta.days == 1:
		return 'tomorrow'
	elif delta.days == -1:
		return 'yesterday'
	return datetime.strftime(date, datefmt)


##### Test views to import data

def import_post(entry):
	user = users.User(email='zanglang@gmail.com')
	p = Post(
			author=user,
			body=entry['body'],
			categories=entry['categories'],
			created_at=datetime.strptime(entry['created_at'], '%Y-%m-%d %H:%M:%S'),
			markup=entry['markup'],
			published=entry['published'],
			slug=entry['slug'],
			title=entry['title'],
			updated_at=datetime.strptime(entry['updated_at'], '%Y-%m-%d %H:%M:%S.%f'))
	p.save()
	logging.info('Imported new blog entry: ' + str(p))

# @app.route('/loaddata')
def load_json():
	import json, os
	basepath = os.path.dirname(os.path.realpath(__file__))
	with open(os.path.join(basepath, 'blog.json')) as f:
		for entry in json.load(f):
			entry = entry['fields']
			deferred.defer(import_post, entry=entry)

	return "Queued tasks"
