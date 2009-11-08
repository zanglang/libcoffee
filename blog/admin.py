from django import forms
from django.contrib import admin
from blog.models import Category, Post
from blog.forms import PostForm
from comments.models import Comment


class CommentInline(admin.TabularInline):
	model = Comment
	fk_name = 'content_object'
	extra = 0

	class CommentForm(forms.ModelForm):
		comment = forms.CharField(label='Comment', widget=forms.Textarea(attrs={
			'cols': '40', 'rows': '10', 'style': 'height:6em',
			'class': 'vLargeTextField'}))
		class Meta:
			model = Comment
			fields = ('content_object', 'comment', 'is_public', 'is_removed')
	form = CommentForm


class PostAdmin(admin.ModelAdmin):
	form = PostForm
	list_display = ('title', 'author', 'created_at', 'updated_at', 'published')
	list_filter = ('author', 'created_at', 'updated_at', 'published')
	search_fields = ('title', 'body')
	date_hierarchy = 'updated_at'
	prepopulated_fields = {"slug": ("title",)}
	inlines = [CommentInline, ]
	actions = ['publish']

	def publish(self, request, queryset):
		from google.appengine.ext import db
		for p in queryset:
			p.published = True
		db.put(queryset)


admin.site.register(Category)
admin.site.register(Post, PostAdmin)
