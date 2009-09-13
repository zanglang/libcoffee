from django.shortcuts import get_object_or_404
from django.views.generic import list_detail
from djangoblog.blog.models import *

def post_list(request, page=0):
	return list_detail.object_list(
		request,
		queryset = Post.objects.filter(published=True),
		paginate_by = 1,
		page = page)

def category_list(request):
	return list_detail.object_list(
		request,
		queryset = Category.objects.all(),
		template_name = 'blog/category_list.html')

def category_detail(request, slug):
	category = get_object_or_404(Category, slug__iexact=slug)
	
	return list_detail.object_list(
		request,
		queryset = category.post_set.filter(published=True),
		extra_context = {'category': category},
		template_name = 'blog/post_list.html')
