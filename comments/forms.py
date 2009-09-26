
from django import forms
from django.contrib.comments.forms import CommentForm

class CustomCommentForm(CommentForm):
	url = forms.URLField(label = "URL", initial = "http://", required = False)
	honeypot = forms.CharField(required = False, widget = forms.widgets.HiddenInput())