from django.conf import settings
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.core.mail import send_mail
from django.db.models.signals import post_save

from akismet import Akismet
from comments.forms import CommentForm
from comments.models import Comment
from comments.signals import comment_was_posted, comment_will_be_posted
from google.appengine.api import mail, xmpp
import logging

def get_model():
	return Comment

def get_form():
	return CommentForm

def get_form_target():
    return urlresolvers.reverse("comments.post_comment")


def new_comment_notify(sender, comment, request, *args, **kwargs):
	#if request.user.is_staff: return # don't bother to notify
	logging.debug('sending mail for new comment')
	message = '%s left a comment:\n\n%s' % (comment.user_name, comment.comment)
	try:
		status = xmpp.send_message(settings.ADMIN_EMAIL, message)
		logging.debug('Sent XMPP message status: %s' % status)
		if status != xmpp.NO_ERROR:
			mail.send_mail(sender=settings.ADMIN_EMAIL,
					to=settings.ADMIN_EMAIL,
					subject='New comment on %s' % comment.content_object.title,
					body=message)
	except:
		logging.warning('Error sending notification', exc_info=True)
		
		

def new_comment_check(sender, comment, request, *args, **kwargs):
	if request.user.is_staff: return # don't bother to check
	ak = Akismet(
		#key = settings.AKISMET_API_KEY,
		key = settings.TYPEPAD_API_KEY,
		blog_url = 'http://%s/' % Site.objects.get_current().domain
	)
	ak.baseurl = 'api.antispam.typepad.com/1.1/'
	if ak.verify_key():
		data = {
			'user_ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
			'user_agent': request.META.get('HTTP_USER_AGENT', ''),
			'referrer': request.META.get('HTTP_REFERER', ''),
			'comment_type': 'comment',
			'comment_author': comment.user_name.encode('utf-8'),
			'comment_author_url': comment.user_url.encode('utf-8'),
			'comment_author_email': comment.user_email.encode('utf-8'),			
		}
		if ak.comment_check(comment.comment.encode('utf-8'), data=data, build_data=True):
			logging.info('marking comment as possibly spam')
			comment.is_public = False
		else:
			logging.debug('comment is ham')


comment_will_be_posted.connect(new_comment_check, dispatch_uid='comments-spam')
comment_was_posted.connect(new_comment_notify, dispatch_uid='comments')