from django.contrib.comments.models import Comment
from django.core.mail import send_mail
from django.db.models.signals import post_save
from comments.forms import CustomCommentForm
from django.contrib.comments.signals import comment_was_posted

def get_form():
	return CustomCommentForm

def new_comment_notify(sender, comment, request, *args, **kwargs):
	subject = 'New comment on %s' % comment.content_object.title
	message = '%s wrote:\n\n%s' % (comment.user_name, comment.comment)
	send_mail(subject, message, 'noreply@libcoffee.net', ['admin@libcoffee.net'])
	
def new_comment_check(sender, comment, request, *args, **kwargs):
	from django.contrib.sites.models import Site
	from django.conf import settings
	try:
		from akismet import Akismet
	except:
		return
	
	ak = Akismet(
		key = settings.AKISMET_API_KEY,
		blog_url = 'http://%s/' % Site.objects.get(pk = settings.SITE_ID).domain
	)
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
			print('marking comment as spam')
			comment.flags.create(
				user=comment.content_object.author,
				flag='spam'
			)
			comment.is_public = False
			comment.save()


comment_was_posted.connect(new_comment_check, dispatch_uid='comments-spam')
comment_was_posted.connect(new_comment_notify, dispatch_uid='comments')