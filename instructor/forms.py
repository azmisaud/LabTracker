from django import forms
from django.contrib.auth.forms import PasswordChangeForm

from instructor.models import Instructor

class InstructorLoginForm(forms.Form):
    username=forms.CharField(max_length=50)
    password=forms.CharField(widget=forms.PasswordInput)

class InstructorChangePasswordForm(PasswordChangeForm):
    def __init__(self,user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.user = user
