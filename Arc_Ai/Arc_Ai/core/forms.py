from django import forms

class DriveUploadForm(forms.Form):
    file = forms.FileField()
