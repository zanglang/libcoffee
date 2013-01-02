# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models

class SocialEvent(models.Model):
	guid = models.CharField(required=True)
	timestamp = models.DateTimeField()

	class Meta:
		ordering = ('-timestamp',)

class Tweet(SocialEvent):
	tweet = models.TextField()
	text_property = 'tweet'

	def __unicode__(self):
		return u'%s' % self.tweet

	def get_absolute_url(self):
		TWEET_PERMALINK = 'http://twitter.com/%s/statuses/%d'
		return TWEET_PERMALINK % (settings.TWITTER_USERNAME, self.guid)
