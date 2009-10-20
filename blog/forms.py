from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime

from blog.models import *

class PostForm(forms.ModelForm):
	body = forms.CharField(widget=forms.Textarea(attrs={
			'cols': '40', 'rows': '10', 'style': 'height:400px', 
			'class': 'vLargeTextField'}))
	class Meta:
		model = Post


class UploadFixtureForm(forms.Form):
	file = forms.FileField()
	secondary = forms.BooleanField(label="Secondary fixtures", required=False)