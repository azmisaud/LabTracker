from django import forms
from .models import Problem


class ProblemForm(forms.ModelForm):
    """
    Form for creating or updating a Problem instance.

    This form allows teachers to submit or update problem details, including the course, semester, week,
    problem number, description, and an optional image. It provides enhanced form field presentation using custom widgets.

    Fields:
        course (Select): Dropdown for selecting the course related to the problem.
        semester (NumberInput): Numeric input for specifying the semester in which the problem is assigned.
        week (NumberInput): Numeric input for specifying the week number during which the problem is relevant.
        problemNumber (TextInput): Text field for entering the problem number.
        description (Textarea): Text area for providing a detailed description of the problem.
        image (ClearableFileInput): Optional file input for uploading an image related to the problem.

    Meta:
        model (Problem): The form is based on the `Problem` model.
        fields (list): The fields displayed in the form include `course`, `semester`, `week`, `problemNumber`, `description`, and `image`.
        widgets (dict): Custom widgets are used to apply CSS classes for enhanced styling of form fields.

    Widgets:
        - course (Select): Rendered as a dropdown list with a Bootstrap `form-control` class.
        - semester (NumberInput): Numeric input field with a `form-control` class for improved UI.
        - week (NumberInput): Numeric input field with a `form-control` class.
        - problemNumber (TextInput): Text input field with a `form-control` class and a placeholder "Problem".
        - description (Textarea): Text area for description input with a `form-control` class.
        - image (ClearableFileInput): File input field for image uploads with a `form-control` class.
    """

    class Meta:
        model = Problem
        fields = ['course', 'semester', 'week', 'problemNumber', 'description', 'image']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control'}),
            'week': forms.NumberInput(attrs={'class': 'form-control'}),
            'problemNumber': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Problem'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
