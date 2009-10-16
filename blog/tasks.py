from django.contrib.sessions.models import Session
from django.core.management import call_command
from django.http import HttpResponse
from django.utils.text import compress_string
from google.appengine.api import mail
from cStringIO import StringIO
from datetime import datetime
import logging, sys
import urllib2, xmlrpclib


def send_trackback(type, source, target, payload=None):
	if type == 'trackback':
		resp = urllib2.urlopen(target, payload)
		logging.debug(resp.read())
	elif type == 'pingback':
		proxy = xmlrpclib.ServerProxy(target)
		proxy.pingback.ping(source, target)
	return HttpResponse('OK')


def run_backup(request):
	logging.info('Starting mail backup')
	# rewire stdout to string buffer
	tmp = sys.stdout
	sys.stdout = data = StringIO()
	call_command('dumpdata', verbose=2, indent=4)
	sys.stdout = tmp
	# done. forward dump to mail service
	logging.info('Backup done. Generated %d bytes.' % len(data.getvalue()))
	# recompress
	data = compress_string(data.getvalue())
	logging.info('Compressed to %d bytes.' % len(data))
	mail.send_mail(sender='zanglang@gmail.com', to='zanglang@gmail.com',
				subject='Libcoffee.net Backup for %s' % str(datetime.now()),
				body='See compressed attachment.',
				attachments=(('test.txt', data),))
	logging.info('Mail sent to admin')
	return HttpResponse('OK')


def maintenance(request):
	logging.info('Deleting expired sessions')
	for s in Session.all().filter('expiry <', datetime.now()):
		s.delete()
	return HttpResponse('OK')

		