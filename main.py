"""
Primary application
"""

import os, sys
from flask import Flask, redirect, render_template, Response, url_for
from flaskext.gae_mini_profiler import GAEMiniProfiler
from google.appengine.ext import ereporter


basepath = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(basepath, 'lib'))

app = Flask('libcoffee')
app.config.from_object('settings')

# Enable profiler (enabled in non-production environ only)
if os.environ.get('SERVER_SOFTWARE', '').startswith('Dev'):
	GAEMiniProfiler(app)

# Enable error reporter
ereporter.register_logger()

from blog import app as blog_app
app.register_blueprint(blog_app, url_prefix='/blog')

from flatpages import app as flatpages_app, register_flatpages
app.register_blueprint(flatpages_app, url_prefix='/pages')
register_flatpages(app)


##### Extra views

@app.route('/')
def index():
	return redirect(url_for('blog.index'))

@app.route('/_ah/warmup')
def warmup():
	"""App Engine warmup handler
	See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests
	"""
	return 'OK'

@app.route('/sitemap.xml')
def sitemap():
	"""Join sitemaps by all registered blueprints"""

	from lxml import etree
	root = etree.Element('urlset', { 'attr': 'http://www.sitemaps.org/schemas/sitemap/0.9' })

	for endpoint, view_func in app.view_functions.iteritems():
		if view_func != sitemap and endpoint.endswith('.sitemap'):
			resp = view_func()
			if resp._status_code == 200:
				for r in resp.response:
					xml = etree.fromstring(r)
					root.extend(xml.getchildren())

	if not len(root):
		return Response('Regenerating sitemap.xml, please come back later.', status=307)

	return Response(etree.tostring(root, encoding='utf-8',
			pretty_print=True, xml_declaration=True), mimetype='text/xml')


@app.route('/_gen_sitemap', methods=['GET', 'POST'])
def generate_sitemap():
	for endpoint, view_func in app.view_functions.iteritems():
		if view_func != generate_sitemap and endpoint.endswith('.generate_sitemap'):
			view_func()
	return 'OK'

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
	return render_template('500.html'), 500
