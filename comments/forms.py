
from django import forms
from django.contrib.comments.forms import CommentForm

class CustomCommentForm(CommentForm):
	honeypot = forms.CharField(required = False, widget = forms.widgets.HiddenInput())
	auth_type = forms.CharField(required = False, widget = forms.widgets.HiddenInput())
	
	def get_comment_create_data(self):
		data = super(CustomCommentForm, self).get_comment_create_data()
		return data
