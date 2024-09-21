from django import forms
from .models import Teacher

class TeacherLoginForm(forms.Form):
    """
    A form for teachers to log in.

    This form includes fields for selecting a teacher from the database and
    entering a password. It is designed to authenticate teachers based on their
    selected name and password.
    """

    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.all(),
        label="Select Your Name",
        help_text="Choose your name from the list of registered teachers."
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Password",
        help_text="Enter your password for authentication."
    )
