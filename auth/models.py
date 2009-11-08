from django.contrib import admin
from django.contrib.auth.models import User
from google.appengine.ext import db

class UserMapping(db.Model):
	user = db.ReferenceProperty(User)
	google_id = db.StringProperty(verbose_name='Google ID', multiline=False)
	#identities = KeyListProperty()

class UserMappingAdmin(admin.ModelAdmin):
	list_display = ('user', 'google_id')

admin.site.register(UserMapping, UserMappingAdmin)
