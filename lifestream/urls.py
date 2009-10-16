from django.conf.urls.defaults import *
from lifestream import tasks

urlpatterns = patterns('',
	(r'tasks/update_twitter/$', tasks.update_twitter),
)