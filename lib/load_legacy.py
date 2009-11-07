from django.contrib.auth.models import User
from django.utils import simplejson
from blog.models import *
from comments.models import Comment
from datetime import datetime
import re

time = lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
if User.all().count() == 0:
	raise NotImplementedError # user =.... 
	# user.save()
else:
	user = User.all()[0]

def import_json(request):
	f = open('static/test.json', 'r')
	j = simplejson.load(f)
	f.close()
	for x in j: gen_model(x)
	print 'OK'

def gen_model(json):
	p = Post(slug=json['permalink'] == 'untitled' and \
				re.sub('[^a-zA-Z0-9 ]', '', json['body'][0:16]) \
					.lower().strip().replace(' ','-') or json['permalink'],
			title=json['title'] == 'Untitled' and \
				datetime.strftime(time(json['created']), '%d %b \'%y')
					or json['title'],
			body=json['body'].replace('typo:code', 'code'),
			created_at=time(json['created']),
			updated_at=time(json['updated']),
			published=True,
			markup='Textile',
			author=user)
	for c in json['categories']:
		c2 = Category.all().filter('title = ', c).get()
		if c2 is None:
			c2 = Category(title=c)
			c2.save()
		p.categories.append(c2.key())
	p.save()
	for c in json['comments']:
		c2 = Comment(user_name=c['author'],
					user_email=c['author'].replace(' ','') + '@example.com',
					user_url='url' in c and c['url'] or None,
					comment=c['body'],
					submit_date=time(c['created']),
					content_object=p)
		c2.save()