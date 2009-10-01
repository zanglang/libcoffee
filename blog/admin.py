from django.contrib import admin
from blog.models import *


class PostAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'created_at', 'updated_at', 'published')
	list_filter = ('author', 'created_at', 'updated_at', 'categories', 'published')
	search_fields = ('title', 'body')
	date_hierarchy = 'updated_at'
	filter_horizontal = ['categories']
	prepopulated_fields = {"slug": ("title",)}		
	radio_fields = {'markuptype': admin.VERTICAL}


admin.site.register(Category)
admin.site.register(Post, PostAdmin)