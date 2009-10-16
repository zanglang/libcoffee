from django.http import HttpResponse, HttpResponseNotAllowed
from google.appengine.api import xmpp
from google.appengine.api.xmpp import InvalidMessageError
from google.appengine.api import memcache
import logging, pprint


def handler(request):
	if not request.POST:
		return HttpResponseNotAllowed('POSTs only')
	try:
		message = xmpp.Message(request.POST)
		if message.body.startswith('memcache'):
			message.reply(str(memcache.get_stats()))
	except InvalidMessageError, e:
		logging.debug('Invalid XMPP message')
		pass
	return HttpResponse('OK')