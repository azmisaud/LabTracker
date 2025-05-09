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
        widgets = {
            'course': forms.Select(attrs={'id': 'course', 'class': 'form-control'}),
            'semester': forms.Select(attrs={'id': 'semester', 'class': 'form-control'}),
            'week': forms.Select(attrs={'id': 'week', 'class': 'form-control'}),
            'last_date': forms.DateInput(attrs={'id': 'last_date', 'type': 'date', 'class': 'form-control'}),
        }

    def save(self, commit=True):
        """
        Override the save method to handle the case when a LastDateOfWeek with the same course, semester, and week exists.
        If it exists, update the last_date. If it does not exist, create a new record.
        """
        # Check if this combination already exists
        course = self.cleaned_data['course']
        semester = self.cleaned_data['semester']
        week = self.cleaned_data['week']
        last_date = self.cleaned_data['last_date']

        # Try to get the existing record
        week_date, created = LastDateOfWeek.objects.get_or_create(
            course=course,
            semester=semester,
            week=week,
            defaults={'last_date': last_date}
        )

        if not created:  # If it already exists, update the last_date
            week_date.last_date = last_date
            week_date.save()

        return week_date
