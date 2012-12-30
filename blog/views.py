import logging
from datetime import datetime, timedelta
from flask import abort, render_template, request

from blog import app
from blog.models import Post
from blog.paginator import Paginator


POSTS_PER_PAGE = 5

def get_posts(year, month=None, day=None, slug=None):
	queryset = Post.objects_published().order('-created_at')
	date = datetime(int(year), month and int(month) or 1, day and int(day) or 1)
	if date > datetime.now():
		abort(404)
	date2 = timedelta(days=(month is None and 365 or day is None and 31 or 1))
	if slug:
		queryset = queryset.filter('slug =', slug)
	return queryset.filter('created_at >=', date) \
				.filter('created_at <', date + date2)


@app.route('/')
def index():
	p = Post.objects_published().order('-created_at')[:POSTS_PER_PAGE]
	return render_template('post_list.html', posts=p)


@app.route('/<int:year>/', defaults={ 'month': None, 'day': None })
@app.route('/<int:year>/<int:month>/', defaults={ 'day': None })
@app.route('/<int:year>/<int:month>/<int:day>/')
def post_list_by_date(year, month, day):
	p = get_posts(year, month, day)

	page = request.args.get('page')
	if page and page.isdigit():
		page = int(page)
		if page < 1:
			abort(404)
		p = p[(page - 1) * POSTS_PER_PAGE : page * POSTS_PER_PAGE]
		if not p and page != 1:
			abort(404)
	else:
		page = 1

	return render_template('post_list.html', posts=p,
			pagination=Paginator(page, POSTS_PER_PAGE, p.count()))


@app.route('/<int:year>/<int:month>/<int:day>/<slug>/')
def post_detail(year, month, day, slug):
	p = get_posts(year, month, day, slug)
	try:
		if type(p) is list: p = p[0]
		else: p = p.get()
	except:
		logging.exception('Could not load post', exc_info=True)
		abort(500)
	return render_template('post_detail.html', post=p)
