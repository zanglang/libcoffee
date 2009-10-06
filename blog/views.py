from django.views.decorators.cache import cache_page
from django.views.generic import list_detail
from blog.models import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
from ragendja.dbutils import get_object_or_404

POSTS_PER_PAGE = 10


@cache_page(60 * 15)
def post_list(request, page=0):
	return list_detail.object_list(
		request,
		queryset = Post.objects_published().order('-created_at'),
		paginate_by = POSTS_PER_PAGE,
		page = page)


@cache_page(60 * 15)
def post_detail(request, year, month, day, slug):
	date = datetime(int(year), int(month), int(day))
	return list_detail.object_detail(
		request,
		queryset = Post.objects_published().filter('created_at >=', date)
				.filter('created_at <', date + relativedelta(days=+1))
				.order('-created_at'),
		slug = slug,
		slug_field = 'slug',
		template_name = 'blog/post_detail.html')
	
	
def post_archive_year(request, year, page=0):
	date = datetime(int(year), 1, 1)
	return list_detail.object_list(
		request,
		queryset = Post.objects_published().filter('created_at >=', date)
			.filter('created_at <', date + relativedelta(years=+1))
			.order('-created_at'),
		paginate_by = POSTS_PER_PAGE,
		page = page)


def post_archive_month(request, year, month, page=0):
	date = datetime(int(year), int(month), 1)
	return list_detail.object_list(
		request,
		queryset = Post.objects_published().filter('created_at >=', date)
				.filter('created_at <', date + relativedelta(months=+1))
				.order('-created_at'),
		paginate_by = POSTS_PER_PAGE,
		page = page)


def post_archive_day(request, year, month, day, page=0):
	date = datetime(int(year), int(month), int(day))
	return list_detail.object_list(
		request,
		queryset = Post.objects_published().filter('created_at >=', date)
				.filter('created_at <', date + relativedelta(days=+1))
				.order('-created_at'),
		paginate_by = POSTS_PER_PAGE,
		page = page)


def category_list(request):
	return list_detail.object_list(
		request,
		queryset = Category.all(),
		template_name = 'blog/category_list.html')
 
 
def category_detail(request, slug):
	category = get_object_or_404(Category, 'title =', slug)
	return list_detail.object_list(
		request,
		queryset = Post.objects_published()
				.filter('categories =', category.key())
				.order('-created_at'),
		paginate_by = POSTS_PER_PAGE,
		page = page,
		template_name = 'blog/post_list.html')
