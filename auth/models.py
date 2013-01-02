from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

class UserMapping(models.Model):
	user = models.ForeignKey(User)
	google_id = models.CharField(verbose_name='Google ID', multiline=False)
	#identities = KeyListProperty()

class UserMappingAdmin(admin.ModelAdmin):
	list_display = ('user', 'google_id')

admin.site.register(UserMapping, UserMappingAdmin)
