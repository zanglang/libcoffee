from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpResponse
from google.appengine.ext import db
from lifestream.models import *
from datetime import datetime
import feedparser
import logging, re


def update_twitter(request):
	TWITTER_URL = 'https://twitter.com/statuses/user_timeline/%s.rss' % \
				settings.TWITTER_USERNAME	
	data = feedparser.parse(TWITTER_URL)
	if data.has_key('bozo_exception'):
		logging.warning('updater_twitter failed: %s' % str(data['bozo_exception']))
		return HttpResponse('No data')
	
	pattern = re.compile(r'^http://twitter.com/.*?/statuses/(\d+)$')
	tweets = dict()
	for d in data['entries']: tweets[pattern.search(d['id']).groups()[0]] = d
	tweeted = [t.guid for t in Tweet.all().filter('guid IN', tweets.keys())]
	logging.debug(tweeted)
	not_tweeted = [t for t in tweets.keys() if t not in tweeted]
	logging.debug(not_tweeted)
	if not len(not_tweeted):
		return HttpResponse('Nothing to save')
	
	s = Site.objects.get_current()
	batch = []
	for t in not_tweeted:
		tweet = Tweet(guid=t)
		tweet.tweet = tweets[t]['summary']
		tweet.timestamp = datetime(*tweets[t]['updated_parsed'][:6])
		batch.append(tweet)
	logging.debug(batch)
	db.put(batch)
	return HttpResponse('OK')