from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from comments.models import Comment

class CommentsAdmin(admin.ModelAdmin):
	fieldsets = (
		(None,
		   # {'fields': ('content_type', 'object_pk', 'site')}
		   {'fields': ('site',)}
		),
		(_('Content'),
		   {'fields': ('user', 'user_name', 'user_email', 'user_url', 'comment')}
		),
		(_('Metadata'),
		   {'fields': ('user_type', 'submit_date', 'ip_address', 'is_public', 'is_removed')}
		),
	 )

	list_display = ('name', 'ip_address', 'submit_date', 'is_public', 'is_removed')
	list_filter = ('submit_date', 'site', 'is_public', 'is_removed')
	date_hierarchy = 'submit_date'
	ordering = ('-submit_date',)
	search_fields = ('comment', 'user__username', 'user_name', 'user_email', 'user_url', 'ip_address')
	actions = ['toggle_public', 'mark_as_removed']
	
	def toggle_public(self, request, queryset):
		from google.appengine.ext import db
		for p in queryset:
			p.is_public = not p.is_public
		db.put(queryset)
		
	def mark_as_removed(self, request, queryset):
		from google.appengine.ext import db
		for p in queryset:
			p.is_removed = True
		db.put(queryset)

# Only register the default admin if the model is the built-in comment model
# (this won't be true if there's a custom comment app).
#if get_model() is Comment:
admin.site.register(Comment, CommentsAdmin)
