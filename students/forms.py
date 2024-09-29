from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Student
import requests


class StudentSignUpForm(UserCreationForm):
    """
    Form for student sign-up, extending the UserCreationForm. This form includes
    additional fields specific to the Student model such as enrollment number,
    faculty number, course, semester, and date of birth.

    Validates whether the provided GitHub username exists, and whether a
    repository exists for the selected course and semester.
    """

    # Additional fields specific to student sign-up
    enrollment_number = forms.CharField(max_length=20, required=True)
    faculty_number = forms.CharField(max_length=20, required=True)
    course = forms.ChoiceField(choices=Student.COURSE_CHOICES)
    semester = forms.ChoiceField(choices=Student.SEMESTER_CHOICES)

    # Date of birth field with a DateInput widget for date selection
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )

    class Meta:
        """
        Meta options for the form.
        Specifies that the model being used is the Student model,
        and defines the fields to be displayed.
        """
        model = Student
        fields = (
            'username', 'first_name', 'last_name', 'enrollment_number',
            'faculty_number', 'date_of_birth', 'course', 'semester',
            'password1', 'password2'
        )

    def clean(self):
        """
        Overrides the default clean method to perform additional validation.

        - Checks if the GitHub username exists using the GitHub API.
        - Checks if a repository exists on GitHub for the selected course and semester.
        If either the username or repository does not exist, appropriate validation
        errors are raised.

        Returns:
            dict: The cleaned data after validation.
        """
        cleaned_data = super().clean()

        # Fetch the necessary fields from the cleaned data
        username = cleaned_data.get('username')
        course = cleaned_data.get('course')
        semester = cleaned_data.get('semester')

        # Remove any periods from the course code for repository name formatting
        formatted_course = course.replace('.', '') if course else None

        # Validate the GitHub username
        if username:
            url = f"https://api.github.com/users/{username}"
            response = requests.get(url)
            if response.status_code != 200:
                # If the GitHub user does not exist, raise a validation error
                self.add_error('username', 'GitHub user does not exist')
                return cleaned_data

        # Validate if the repository exists for the selected course and semester
        if username and formatted_course and semester:
            repo_name = f"{formatted_course}Lab{semester}"
            url = f"https://api.github.com/repos/{username}/{repo_name}"
            response = requests.get(url)
            if response.status_code != 200:
                # If the repository does not exist, raise a validation error
                self.add_error('username', f"GitHub repository '{repo_name}' does not exist.")

        return cleaned_data


class EnrollmentFacultyForm(forms.Form):
    """
    Form to capture enrollment number and faculty number for student authentication.

    This form is used when students need to verify their identity by providing their
    enrollment number and faculty number, typically for password reset or other verification processes.

    Fields:
    - enrollment_number (CharField): A required field to input the student's enrollment number.
      Max length is 11 characters.
    - faculty_number (CharField): A required field to input the student's faculty number.
      Max length is 15 characters.
    """
    enrollment_number = forms.CharField(max_length=11, required=True)
    faculty_number = forms.CharField(max_length=15, required=True)


class DateOfBirthForm(forms.Form):
    """
    Form to capture the student's date of birth for additional verification.

    This form is typically used as a secondary layer of verification, where the student
    provides their date of birth. It uses an HTML5 date input field.

    Fields:
    - date_of_birth (DateField): A required field where students enter their date of birth.
      The widget is an HTML5 date input for better UX.
    """
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))


class PasswordResetForm(forms.Form):
    """
    Form to capture and validate the new password during a password reset process.

    This form requires the student to input the new password and confirm it to ensure
    the new password is entered correctly.

    Fields:
    - new_password (CharField): A required field for the student's new password. The input is
      hidden using a PasswordInput widget.
    - confirm_password (CharField): A required field to confirm the new password, also hidden
      with a PasswordInput widget.
    """
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
