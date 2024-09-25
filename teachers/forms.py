from django import forms
from .models import Teacher, WeekLastDate


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


class WeekLastDateForm(forms.ModelForm):
    """
    A form for creating or updating `WeekLastDate` records.

    This form is tied to the `WeekLastDate` model and is used to input or update the last date for a specific course, semester, and week.
    It includes custom widgets to enhance the user experience when selecting values for the course, semester, week, and last date.

    Meta:
        model (WeekLastDate): Specifies the model that this form is associated with.
        fields (list): Defines the fields to be displayed in the form. These include:
            - `course`: The course associated with the week (e.g., BCA, MCA, MSC).
            - `semester`: The semester associated with the week.
            - `week`: The week number.
            - `last_date`: The last date for the specified week.

    Widgets:
        - `course`: A dropdown select menu styled with Bootstrap classes, with the ID `course`.
        - `semester`: A dropdown select menu styled with Bootstrap classes, with the ID `semester`.
        - `week`: A dropdown select menu styled with Bootstrap classes, with the ID `week`.
        - `last_date`: A date picker input field with the ID `last_date`, where the input type is set to `date`.

    Attributes:
        model (WeekLastDate): The model that the form is associated with.
        fields (list): The specific fields included in the form.
        widgets (dict): Custom widgets for styling and user input enhancements.

    Example Usage:
        - This form can be used in views where teachers or administrators set or update the last submission dates for assignments or tasks.

    Example:
        >>> form = WeekLastDateForm()
        >>> form.as_p()  # Render the form in HTML with the fields and custom widgets.
    """

    class Meta:
        model = WeekLastDate
        fields = ['course', 'semester', 'week', 'last_date']

        # Custom widgets for enhancing the appearance and user input experience
        widgets = {
            'course': forms.Select(attrs={'id': 'course', 'class': 'form-control'}),
            'semester': forms.Select(attrs={'id': 'semester', 'class': 'form-control'}),
            'week': forms.Select(attrs={'id': 'week', 'class': 'form-control'}),
            'last_date': forms.DateInput(attrs={'id': 'last_date', 'type': 'date'}),
        }

