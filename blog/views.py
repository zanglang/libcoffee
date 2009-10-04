from django.views.generic import list_detail
from blog.models import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
from ragendja.dbutils import get_object_or_404


def post_list(request, page=0):
	return list_detail.object_list(
		request,
		queryset = Post.objects_published(),
		paginate_by = 10,
		page = page)


def post_archive_year(request, year, page=0):
	date = datetime(int(year), 1, 1)
	return list_detail.object_list(
		request,
		queryset = Post.objects_published().filter('created_at >=', date)
			.filter('created_at <', date + relativedelta(years=+1)),
		paginate_by = 10,
		page = page)


def post_archive_month(request, year, month, page=0):
	date = datetime(int(year), int(month), 1)
	return list_detail.object_list(
		request,
		queryset = Post.objects_published().filter('created_at >=', date)
				.filter('created_at <', date + relativedelta(months=+1)),
		paginate_by = 10,
		page = page)


def post_archive_day(request, year, month, day, page=0):
	date = datetime(int(year), int(month), int(day))
	return list_detail.object_list(
		request,
		queryset = Post.objects_published().filter('created_at >=', date)
				.filter('created_at <', date + relativedelta(days=+1)),
		paginate_by = 10,
		page = page)


def post_detail(request, year, month, day, slug):
	date = datetime(int(year), int(month), int(day))
	return list_detail.object_detail(
		request,
		queryset = Post.objects_published().filter('created_at >=', date)
				.filter('created_at <', date + relativedelta(days=+1)),
		slug = slug,
		slug_field = 'slug',
		template_name = 'blog/post_detail.html')


def category_list(request):
	return list_detail.object_list(
		request,
		queryset = Category.all(),
		template_name = 'blog/category_list.html')
 
 
def category_detail(request, slug):
	category = get_object_or_404(Category, 'title =', slug)
	return list_detail.object_list(
		request,
		queryset = Post.all().filter('categories =', category.key()),
		template_name = 'blog/post_list.html')
