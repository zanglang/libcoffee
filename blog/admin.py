from django.contrib import admin
from blog.models import *


class PostAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'created_at', 'updated_at', 'published')
	list_filter = ('author', 'created_at', 'updated_at', 'published')
	search_fields = ('title', 'body')
	date_hierarchy = 'updated_at'
	prepopulated_fields = {"slug": ("title",)}
	#radio_fields = {'markup': admin.VERTICAL}


admin.site.register(Category)
admin.site.register(Post, PostAdmin)