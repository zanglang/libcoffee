from django.conf.urls.defaults import *

urlpatterns = patterns('comments.views',
    url(r'^post/$', 'post_comment', name='comments-post-comment'),
    url(r'^posted/$', 'comment_done', name='comments-comment-done'),
    url(r'^cr/(?P<id>.+)/$', 'comment_view', name='comments-url-redirect')
)