from django.contrib.admin.views.decorators import staff_member_required
from django.core import serializers
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.views.decorators.cache import cache_page, never_cache
from django.views.generic import list_detail
from blog.models import *
from datetime import datetime, timedelta
import logging
from memoize import memoize
from ragendja.dbutils import get_object_or_404


POSTS_PER_PAGE = 5
POST_CACHE_TIME = 60*60*24


@memoize()
def get_posts(year, month=None, day=None, slug=None):
	queryset = Post.objects_published().order('-created_at')
	date = datetime(int(year), month and int(month) or 1, day and int(day) or 1)
	if date > datetime.now():
		raise Http404
	date2 = timedelta(days=(month is None and 365 or day is None and 31 or 1))
	if slug:
		queryset = queryset.filter('slug =', slug)
	return queryset.filter('created_at >=', date) \
				.filter('created_at <', date + date2)

	
@cache_page(POST_CACHE_TIME)
def post_list(request, page=0):
	return list_detail.object_list(
		request,
		queryset = Post.objects_published().order('-created_at'),
		paginate_by = POSTS_PER_PAGE,
		page = page)


def post_detail(request, year, month, day, slug):
	p = get_posts(year, month, day, slug)
	try:
		if type(p) is list: p = p[0]
		else: p = p.get()
	except:
		logging.warning('', exc_info=True)
		raise Http404
	return render_to_response('blog/post_detail.html', {
			'object': p
		}, context_instance=RequestContext(request))


@cache_page(POST_CACHE_TIME)
def post_archive_year(request, year, page=0):
	date_list = {}
	queryset = get_posts(year)
	for p in queryset:
		d = datetime(p.created_at.year, p.created_at.month, 1)
		if not date_list.has_key(d):
			date_list[d] = set()
		date_list[d].add(p)
	return list_detail.object_list(
		request,
		queryset = queryset,
		template_name = 'blog/post_archive_year.html',
		extra_context={'year': year,
					'date_list': date_list })


@cache_page(POST_CACHE_TIME)
def post_archive_month(request, year, month, page=0):
	date = datetime(int(year), int(month), 1)
	return list_detail.object_list(
		request,
		queryset = get_posts(year, month),
		paginate_by = POSTS_PER_PAGE,
		page = page,
		template_name = 'blog/post_archive_month.html',
		extra_context={'month': date})


@cache_page(POST_CACHE_TIME)
def post_archive_day(request, year, month, day, page=0):
	date = datetime(int(year), int(month), int(day))
	return list_detail.object_list(
		request,
		queryset = get_posts(year, month, day),
		paginate_by = POSTS_PER_PAGE,
		page = page,
		template_name = 'blog/post_archive_day.html',
		extra_context={'day': date})


@cache_page(POST_CACHE_TIME)
def category_list(request):
	return list_detail.object_list(
		request,
		queryset = Category.all().order('title'),
		template_name = 'blog/category_list.html')


@cache_page(POST_CACHE_TIME)
def category_detail(request, slug, page=0):
	category = Category.all().filter('slug = ', slug).get() or \
			get_object_or_404(Category, 'title =', slug.capitalize())
	return list_detail.object_list(
		request,
		queryset = Post.objects_published()
				.filter('categories =', category.key())
				.order('-created_at'),
		paginate_by = POSTS_PER_PAGE,
		page = page,
		template_name = 'blog/category_detail.html',
		extra_context={'category': category})


@never_cache
@staff_member_required
def post_preview(request, object_id):
	return list_detail.object_detail(request,
		object_id = object_id,
		queryset = Post.all())


@staff_member_required
def fixture_restore(request):
	from blog.forms import UploadFixtureForm
	from google.appengine.ext import db
	
	if request.method == 'POST':
		form = UploadFixtureForm(request.POST, request.FILES)
		if form.is_valid():
			f = request.FILES['file'].read()
			logging.info('Start restoring fixtures. size is %d' % len(f))
			# django dumpdata fixtures
			if not request.POST.has_key('secondary'):
				data = serializers.deserialize('json', f)
				for d in data:
					logging.debug(d)
				db.put(data)
			else:
				# secondary fixtures
				batch = []
				models = set()				
				data = simplejson.loads(f)
				logging.info('Loaded %d json objects from fixture' % len(data))
				for d in data:
					object = db.get(d['pk'])
					if not object:
						logging.warning('pk %s not found' % d['pk'])
						continue
					setattr(object, d['field'], d['data'])
					models.add(object._meta.model)
					batch.append(object)
				# last step
				db.put(batch)
				logging.info('Load fixtures done. Models changed: %s' % models)
				
	else:
		form = UploadFixtureForm()
	return render_to_response('blog/fixtures.html', {
			'form': form,
			'request': request
		}, context_instance=RequestContext(request))


@staff_member_required
def fixture_dump(request):
	""" Generates additional fixtures complementary to dumpdata, mainly for
		ragendja's KeyListProperty """
	logging.info('Generating fixture dumps...')
	data = simplejson.dumps([{
			'pk': x.pk,
			'field': 'categories',
			'data': [unicode(y) for y in x.categories]
		} for x in Post.all()], indent=4)
	logging.info('Generated %d bytes in fixture. Dumping...' % len(data))
	response = HttpResponse(data, mimetype='text/json')
	response['Content-Disposition'] = 'attachment; filename=fixtures-%s.json' \
			% datetime.strftime(datetime.now(), '%Y%m%d-%H%M%S')
	return response

	
def redirect_to_blog(request, year=None, month=None, day=None):
	url = '/blog/'
	if year: url += year + '/'
	if month: url += month + '/'
	if day: url += day + '/'	
	return HttpResponsePermanentRedirect(url)
