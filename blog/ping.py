from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from blog.models import Post
from blog.tasks import send_trackback as send_trackback_task
from trackback import registry
from google.appengine.ext.deferred import deferred
import logging, re, urllib, urllib2, xmlrpclib

URL_RE = re.compile(r'\b((https?|ftp|file)://[-A-Z0-9+&@#/%?=~_|!:,.;]*[-A-Z0-9+&@#/%=~_|])', re.IGNORECASE)

def resolver(target_url):
	from django.core.urlresolvers import get_resolver, NoReverseMatch, Resolver404
	from datetime import datetime
	from dateutil.relativedelta import relativedelta
	try:
		urlresolver = get_resolver(None)
		site = Site.objects.get_current()
		func, args, kwargs = urlresolver.resolve(target_url.replace("http://%s" % site.domain, ''))
		date = datetime(int(kwargs['year']), int(kwargs['month']), int(kwargs['day']))
		return Post.objects_published().filter('slug =', kwargs['slug']) \
				.filter('created_at >=', date) \
				.filter('created_at <', date + relativedelta(days=+1)).get()
	except (NoReverseMatch, Resolver404), e:
		return None
	except Exception:
		logging.warn('Couldn\'t resolve url' % target_url, exc_info=True)
		return None
registry.add(resolver, True)


def send_trackback(instance, **kwargs):
	from trackback.utils.parse import discover_pingback_url, discover_trackback_url
	from google.appengine.api.labs import taskqueue
	import copy
	
	if settings.DEBUG: return # disable when debugging
	if not settings.DEBUG and type(instance) is Post \
		and (not instance.published or instance._was_published):
			return
	content = getattr(instance, instance.trackback_content_field_name, '')
	site = Site.objects.get_current()
	urls = URL_RE.findall(content)
	data = {}
	data['url'] = 'http://%s%s' % (site.domain, instance.get_absolute_url())
	data['title'] = unicode(instance)
	data['blog_name'] = site.name
	data['excerpt'] = content[:200]
	payload = urllib.urlencode(data)
	#send_trackback_url = reverse(send_trackback_task)
	
	countdown = 0
	for url, _ in urls:
		try:
			target = discover_trackback_url(url)
			if target:
				ctype = 'trackback'
			else:
				target = discover_pingback_url(url)
				if not target:
					logging.debug('No trackback/pingback service found for %s' % url)
					continue
				ctype = 'pingback'
			countdown += 5
			deferred.defer(send_trackback_task, ctype, data['url'], target,
						payload, _countdown=countdown)
			#		'type': type,
			#		'target': target,
			#		'source': data['url'],
			#		'data': payload })
			
		except:
			logging.error('send_trackback error', exc_info=True)


def send_ping(instance, **kwargs):
	if settings.DEBUG: return # disable when debugging
	if type(instance) is Post:
		if not instance.published or instance._was_published:
			return
	logging.debug('sending rpc pings')
	site = Site.objects.get_current()
	domain = 'http://%s' % site.domain
	instance_url = 'http://%s%s' % (site.domain, instance.get_absolute_url())
	
	URLS = (
		('technorati', 'http://rpc.technorati.com/rpc/ping'),
		('google', 'http://blogsearch.google.com/ping/RPC2'),
		('feedburner', 'http://ping.feedburner.com'),
	)
	for (name, url) in URLS:
		try:
			rpc = xmlrpclib.Server(url);
			result = rpc.weblogUpdates.ping(site.name, domain, instace_url)
			if result['flerror']:
				logging.warn('Error pinging %s (%s). Reason: %s' % 
							(url, name, result['message']))
			else:
				logging.info('pinging %s (%s) successful' % (url, name))
		except Exception:
			logging.debug('Error sending XMLRPC', exc_info=True)
	
	data = urllib.urlencode({
		'hub.url': 'http://%s/blog/feeds/latest/' % site.domain,
		'hub.mode': 'publish'
	})
	response = urllib2.urlopen(settings.HUBBUB_URL, data)
	if response.status_code / 100 != 2:
		logging.warning("Hub ping failed", response.status_code, response.content)
	return


def trackback_check(instance, created, **kwargs):
	from comments.akismet import Akismet	
	if not created: return
	logging.debug('checking trackback for spam')
	ak = Akismet(
		key = settings.TYPEPAD_API_KEY,
		blog_url = 'http://%s/' % Site.objects.get_current().domain
	)
	ak.baseurl = 'api.antispam.typepad.com/1.1/'
	if ak.verify_key():
		data = {
			'user_ip': instance.remote_ip,
			'user_agent': '',
			'comment_type': 'trackback',
			'comment_author': instance.title or instance.blog_name or '',
			'comment_author_url': instance.url or '',
		}
		if not ak.comment_check(instance.excerpt or '', data=data, build_data=True):
			logging.debug('trackback is ham')
			instance.is_public = True
		else:
			logging.warn('marking trackback as spam')
			instance.is_public = False
		instance.save()
