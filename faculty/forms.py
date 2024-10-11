from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from faculty.models import Faculty, LastDateOfWeek

class FacultyLoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)

class ChangePasswordForm(PasswordChangeForm):
    def __init__(self,user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.user = user


class LastDateOfWeekForm(forms.ModelForm):
    class Meta:
        model = LastDateOfWeek
        fields = ['course', 'semester', 'week', 'last_date']

        # Custom widgets for enhancing the appearance and user input experience
        widgets = {
            'course': forms.Select(attrs={'id': 'course', 'class': 'form-control'}),
            'semester': forms.Select(attrs={'id': 'semester', 'class': 'form-control'}),
            'week': forms.Select(attrs={'id': 'week', 'class': 'form-control'}),
            'last_date': forms.DateInput(attrs={'id': 'last_date', 'type': 'date'}),
        }
