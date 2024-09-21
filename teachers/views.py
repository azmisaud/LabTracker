from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .forms import TeacherLoginForm
from .models import Teacher


def teacher_login(request):
    """
    Handles the login process for teachers.

    This view processes both GET and POST requests to handle teacher login.
    It validates the teacher's selection and password, authenticating them if
    the credentials are correct. Upon successful login, the teacher is redirected
    to the dashboard. If the login fails, an error message is displayed.

    Args:
        request (HttpRequest): The HTTP request object, containing metadata
        about the request.

    Returns:
        HttpResponse: Renders the login page with a form for GET requests.
        Redirect: Redirects the teacher to the dashboard upon successful login.
    """

    if request.method == 'POST':
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            teacher = form.cleaned_data['teacher']
            password = form.cleaned_data['password']

            # Extract the teacher's first name and generate the expected password.
            first_name = teacher.name.split()[1]
            expected_password = f"{first_name}@{settings.TEACHER_PASSWORD_BASE}"

            # Authenticate the teacher based on the provided password.
            if password == expected_password:
                # Store teacher's ID in session upon successful login.
                request.session['teacher_id'] = teacher.id
                return redirect('teacher_login')
            else:
                # Display an error message if the password is incorrect.
                messages.error(request, 'Incorrect password.')
    else:
        # If the request is GET, initialize an empty login form.
        form = TeacherLoginForm()

    # Render the login page with the form.
    return render(request, 'teachers/login.html', {'form': form})

