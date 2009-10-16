from django import forms

class UploadFixtureForm(forms.Form):
	file = forms.FileField()
	secondary = forms.BooleanField(label="Secondary fixtures", required=False)