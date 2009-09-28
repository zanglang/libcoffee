from comments.akismet import Akismet
from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from trackback import signals
from trackback.models import Trackback
from trackback.utils.send import send_trackback as send_tb, \
	send_pingback as send_pb
import re
import threading
import xmlrpclib

URL_RE = re.compile(r'http://[^\ ]+', re.IGNORECASE)

def send_trackback(instance, **kwargs):
    if settings.DEBUG: return # disable when debugging
    content = getattr(instance, instance.trackback_content_field_name)
    urls = URL_RE.findall(content)
    data = {}
    site = Site.objects.get_current()
    data['url'] = site.domain + instance.get_absolute_url()
    data['title'] = unicode(instance)
    data['blog_name'] = site.name
    data['excerpt'] = content[:100]
    
    for url in urls:
        print "trackbacking %s" % url
        t = threading.Thread(target=send_tb, args=[url, data,])
        t.start()
        #send_tb(url, data,) # fail_silently=False)
        print "pingbacking %s" % url
        t2 = threading.Thread(target=send_pb, args=[instance.get_absolute_url(), url,])
        t2.start()
        #send_pb(instance.get_absolute_url(), url,)# fail_silently=False)


def send_ping(instance, **kwargs):
	if settings.DEBUG: return # disable when debugging
	print 'sending rpc pings'
	site = Site.objects.get_current()
	URLS = (
		('technorati', 'http://rpc.technorati.com/rpc/ping'),
		('google', 'http://blogsearch.google.com/ping/RPC2'),
	)
	for (name, url) in URLS:
		try:
			rpc = xmlrpclib.Server(url);
			rpc.weblogUpdates.ping(site.name, site.domain)
			print 'pinging %s (%s) successful' % (url, name)
		except Exception as e:
			print e
			pass
	return


def trackback_check(instance, created, **kwargs):
	if not created: return # only spam check when creating
	print 'checking trackback for spam'
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
			print 'trackback is ham'
			instance.is_public = True
			instance.save() # this will retrigger the signal again, remember to filter it
		else:
			print 'marking trackback as spam'
			instance.is_public = False
			instance.save()


signals.send_trackback.connect(send_trackback, dispatch_uid='send-trackback')
signals.send_trackback.connect(send_ping, dispatch_uid='send-ping')
post_save.connect(trackback_check, sender=Trackback, dispatch_uid='trackback-filter')