# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User
from google.appengine.ext import db


class SocialEvent(db.Model):
	guid = db.StringProperty(required=True)
	timestamp = db.DateTimeProperty()

	class Meta:
		ordering = ('-timestamp',)

class Tweet(SocialEvent):
	tweet = db.TextProperty()
	text_property = 'tweet'
	
	def __unicode__(self):
		return u'%s' % self.tweet
	
	def get_absolute_url(self):
		TWEET_PERMALINK = 'http://twitter.com/%s/statuses/%d'
		return TWEET_PERMALINK % (settings.TWITTER_USERNAME, self.guid)