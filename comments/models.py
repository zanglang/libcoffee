import datetime
from django.contrib.auth.models import User
#from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from google.appengine.api import memcache, users
from google.appengine.ext import db
import logging

COMMENT_MAX_LENGTH = getattr(settings,'COMMENT_MAX_LENGTH',3000)

class BaseCommentAbstractModel(db.Model):
    """
    An abstract base class that any custom comment models probably should
    subclass.
    """

    #content_type = FakeModelProperty(ContentType)
    content_object = db.ReferenceProperty(verbose_name='object ID')
    site = db.ReferenceProperty(Site)
    # Content-object field
    #content_type   = models.ForeignKey(ContentType,
    #        verbose_name=_('content type'),
    #        related_name="content_type_set_for_%(class)s")
    #object_pk      = models.TextField(_('object ID'))
    #content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    
    # Metadata about the comment
    #site        = models.ForeignKey(Site)

    class Meta:
        abstract = True

    def get_content_object_url(self):
        """
        Get a URL suitable for redirecting to the content object.
        """
        return urlresolvers.reverse(
            "comments-url-redirect",
            args=(self.pk,)
        )

class Comment(BaseCommentAbstractModel):
    """
    A user comment about some object.
    """

    # Who posted this comment? If ``user`` is set then it was an authenticated
    # user; otherwise at least user_name should have been set and the comment
    # was posted by a non-authenticated user.
    user = db.ReferenceProperty()
    user_name = db.StringProperty(verbose_name='user\'s name')
    user_email = db.EmailProperty(default='')
    user_url = db.StringProperty(verbose_name='user\'s URL')
    comment = db.TextProperty(default='')
    user_type = db.StringProperty() # custom
    
    submit_date = db.DateTimeProperty(verbose_name='date/time submitted')
    ip_address = db.StringProperty(verbose_name='IP address')
    is_public = db.BooleanProperty(default=True)
    is_removed = db.BooleanProperty(default=False)

    def __init__(self, *args, **kw):
        super(Comment, self).__init__(*args, **kw)
        self.facebook_uid = self.user_type == 'facebook' and \
        		self.user_email.split('@')[0] or None

    class Meta:
        db_table = "django_comments"
        ordering = ('submit_date',)
        permissions = [("can_moderate", "Can moderate comments")]
        verbose_name = _('comment')
        verbose_name_plural = _('comments')

    def __unicode__(self):
        return "%s: %s..." % (self.name, self.comment[:50])

    def save(self, force_insert=False, force_update=False):
        if self.submit_date is None:
            self.submit_date = datetime.datetime.now()
        super(Comment, self).save()
        memcache.flush_all()
        
    def delete(self):
        super(Comment, self).delete()
        memcache.flush_all()
        
    def _get_short_id(self):
    	return self.key().id_or_name() # remind self to use this less.
    shortid = property(_get_short_id)

    def _get_userinfo(self):
        """
        Get a dictionary that pulls together information about the poster
        safely for both authenticated and non-authenticated comments.

        This dict will have ``name``, ``email``, and ``url`` fields.
        """
        if not hasattr(self, "_userinfo"):
            self._userinfo = {
                "name"  : self.user_name,
                "email" : self.user_email,
                "url"   : self.user_url
            }
            if self.user:
                u = self.user
                if u.email:
                    self._userinfo["email"] = u.email

                # If the user has a full name, use that for the user name.
                # However, a given user_name overrides the raw user.username,
                # so only use that if this comment has no associated name.
                if u.get_full_name():
                    self._userinfo["name"] = self.user.get_full_name()
                elif not self.user_name:
                    self._userinfo["name"] = u.username
        return self._userinfo
    userinfo = property(_get_userinfo, doc=_get_userinfo.__doc__)

    def _get_name(self):
        return self.userinfo["name"]
    def _set_name(self, val):
        if self.user:
            raise AttributeError(_("This comment was posted by an authenticated "\
                                   "user and thus the name is read-only."))
        self.user_name = val
    name = property(_get_name, _set_name, doc="The name of the user who posted this comment")

    def _get_email(self):
        return self.userinfo["email"]
    def _set_email(self, val):
        if self.user:
            raise AttributeError(_("This comment was posted by an authenticated "\
                                   "user and thus the email is read-only."))
        self.user_email = val
    email = property(_get_email, _set_email, doc="The email of the user who posted this comment")

    def _get_url(self):
        return self.userinfo["url"]
    def _set_url(self, val):
        self.user_url = val
    url = property(_get_url, _set_url, doc="The URL given by the user who posted this comment")

    @permalink
    def get_absolute_url(self):
    	return ('comments-url-redirect', (), { 'id': self.shortid })

    def get_as_text(self):
        """
        Return this comment as plain text.  Useful for emails.
        """
        d = {
            'user': self.user or self.name,
            'date': self.submit_date,
            'comment': self.comment,
            'domain': self.site.domain,
            'url': self.get_absolute_url()
        }
        return _('Posted by %(user)s at %(date)s\n\n%(comment)s\n\nhttp://%(domain)s%(url)s') % d
       
    @staticmethod
    def objects_public():
        return Comment.all().filter('is_public =', True) \
       			.filter('is_removed =', False)
