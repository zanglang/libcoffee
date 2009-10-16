from django import http
from django.conf import settings
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.html import escape
from django.views.decorators.http import require_POST
from google.appengine.api import users
from google.appengine.ext import db
from ragendja.dbutils import get_object_or_404
import logging
import urllib
import textwrap
import comments
from comments import signals


def next_redirect(data, default, default_view, **get_kwargs):
    """
    Handle the "where should I go next?" part of comment views.

    The next value could be a kwarg to the function (``default``), or a
    ``?next=...`` GET arg, or the URL of a given view (``default_view``). See
    the view modules for examples.

    Returns an ``HttpResponseRedirect``.
    """
    next = data.get("next", default)
    if next is None:
        next = urlresolvers.reverse(default_view)
    if get_kwargs:
        joiner = ('?' in next) and '&' or '?'
        next += joiner + urllib.urlencode(get_kwargs)
    return HttpResponseRedirect(next)

def confirmation_view(template, doc="Display a confirmation view."):
    """
    Confirmation view generator for the "comment was
    posted/flagged/deleted/approved" views.
    """
    def confirmed(request):
        comment = None
        if 'c' in request.GET:
            try:
                comment = comments.get_model().objects.get(pk=request.GET['c'])
            except ObjectDoesNotExist:
                pass
        return render_to_response(template,
            {'comment': comment},
            context_instance=RequestContext(request)
        )

    confirmed.__doc__ = textwrap.dedent("""\
        %s

        Templates: `%s``
        Context:
            comment
                The posted comment
        """ % (doc, template)
    )
    return confirmed

class CommentPostBadRequest(http.HttpResponseBadRequest):
    """
    Response returned when a comment post is invalid. If ``DEBUG`` is on a
    nice-ish error message will be displayed (for debugging purposes), but in
    production mode a simple opaque 400 page will be displayed.
    """
    def __init__(self, why):
        super(CommentPostBadRequest, self).__init__()
        if settings.DEBUG:
            self.content = render_to_string("comments/400-debug.html", {"why": why})

def post_comment(request, next=None):
    """
    Post a comment.

    HTTP POST is required. If ``POST['submit'] == "preview"`` or if there are
    errors a preview template, ``comments/preview.html``, will be rendered.
    """
    # Fill out some initial data fields from an authenticated user, if present
    data = request.POST.copy()
    if request.user.is_authenticated():
        if not data.get('name', ''):
            data["name"] = request.user.get_full_name() or request.user.username
        if not data.get('email', ''):
            data["email"] = request.user.email
        if not data.get('url', ''):
            data['url'] = 'http://%s' % Site.objects.get_current().domain

    # Check to see if the POST data overrides the view's next argument.
    next = data.get("next", next)

    # Look up the object we're trying to comment about
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    if ctype is None or object_pk is None:
        return CommentPostBadRequest("Missing content_type or object_pk field.")
    try:
        #model = models.get_model(*ctype.split(".", 1))
        #target = model._default_manager.get(pk=object_pk)
        target = db.get(object_pk)
    except TypeError:
        return CommentPostBadRequest(
            "Invalid content_type value: %r" % escape(ctype))
    except AttributeError:
        return CommentPostBadRequest(
            "The given content-type %r does not resolve to a valid model." % \
                escape(ctype))
    except ObjectDoesNotExist:
        return CommentPostBadRequest(
            "No object matching content-type %r and object PK %r exists." % \
                (escape(ctype), escape(object_pk)))

    # Do we want to preview the comment?
    preview = "preview" in data

    # Construct the comment form
    form = comments.get_form()(target, data=data)

    # Check security information
    if form.security_errors():
        return CommentPostBadRequest(
            "The comment form failed security verification: %s" % \
                escape(str(form.security_errors())))

    # If there are errors or if we requested a preview show the comment
    if form.errors or preview:
        template_list = [
            "comments/%s/%s/preview.html" % tuple(str(target._meta).split(".")),
            "comments/%s/preview.html" % target._meta.app_label,
            "comments/preview.html",
        ]
        return render_to_response(
            template_list, {
                "comment" : form.data.get("comment", ""),
                "form" : form,
                "next": next,
            },
            RequestContext(request, {})
        )

    # Otherwise create the comment
    comment = form.get_comment_object()
    comment.ip_address = request.META.get("REMOTE_ADDR", None)
    if request.user.is_authenticated():
        comment.user = request.user
    #elif users.get_current_user():
    #	comment.user = users.get_current_user()

    # Signal that the comment is about to be saved
    responses = signals.comment_will_be_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )

    for (receiver, response) in responses:
        if response == False:
            return CommentPostBadRequest(
                "comment_will_be_posted receiver %r killed the comment" % receiver.__name__)

    # Save the comment and signal that it was saved
    comment.save()
    signals.comment_was_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )

    return next_redirect(data, next, comment_done, c=comment._get_pk_val())

post_comment = require_POST(post_comment)

comment_done = confirmation_view(
    template = "comments/posted.html",
    doc = """Display a "comment was posted" success page."""
)

def comment_view(request, id):
	if id.startswith('id'):	# because we messed up our keys...
		comment = comments.get_model().get_by_key_name(id)
	else:
		comment = comments.get_model().get_by_id(long(id))
	link = '%s#c%s' % (comment.content_object.get_absolute_url(), id)
	return HttpResponseRedirect(link)