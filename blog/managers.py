from django.db.models import Manager

class PostManager(Manager):
	def published(self):
		return self.get_query_set().filter(published=True)